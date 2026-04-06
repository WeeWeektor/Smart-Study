import json
import random
import time
from concurrent.futures import ThreadPoolExecutor

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import TransactionTestCase, Client

User = get_user_model()


class AuthStressTest(TransactionTestCase):
    """Stress тести для аутентифікації"""

    def setUp(self):
        cache.clear()
        self.stress_users = []
        for i in range(50):
            user = User.objects.create_user(
                email=f'auth_stress_{i}@example.com',
                password='AuthStress123!',
                is_verified_email=True,
                is_active=True
            )
            self.stress_users.append(user)

    def test_massive_concurrent_logins(self):
        """Тест масових одночасних логінів"""
        login_results = []

        def concurrent_login(user_email):
            client = Client()
            start = time.time()

            login_data = {
                'email': user_email,
                'password': 'AuthStress123!'
            }

            try:
                response = client.post('/api/auth/login/',
                                       json.dumps(login_data),
                                       content_type='application/json')
                end = time.time()

                return {
                    'success': response.status_code == 200,
                    'status_code': response.status_code,
                    'time': end - start,
                    'email': user_email
                }
            except Exception as e:
                end = time.time()
                return {
                    'success': False,
                    'status_code': 500,
                    'time': end - start,
                    'email': user_email,
                    'error': str(e)
                }

        with ThreadPoolExecutor(max_workers=25) as executor:
            futures = [executor.submit(concurrent_login, user.email) for user in self.stress_users]

            for future in futures:
                result = future.result()
                login_results.append(result)

        successful_logins = [r for r in login_results if r['success']]
        failed_logins = [r for r in login_results if not r['success']]

        success_rate = len(successful_logins) / len(login_results) if login_results else 0
        avg_login_time = sum(r['time'] for r in successful_logins) / len(successful_logins) if successful_logins else 0

        print(f"🔥 Concurrent logins: {len(successful_logins)}/{len(login_results)} successful")
        print(f"🔥 Success rate: {success_rate:.2%}")
        print(f"🔥 Average login time: {avg_login_time:.3f}s")

        self.assertGreaterEqual(success_rate, 0.90)
        self.assertLess(avg_login_time, 3.0)

        critical_errors = [r for r in failed_logins if r.get('status_code') == 500]
        self.assertLess(len(critical_errors), len(login_results) * 0.05)

    def test_registration_flood(self):
        """Тест flood реєстрацій"""
        registration_results = []

        def flood_registration(index):
            client = Client()
            start = time.time()

            register_data = {
                'name': f'FloodUser{index}',
                'surname': f'Test{index}',
                'email': f'flood_{index}_{random.randint(1000, 9999)}@example.com',
                'password': 'FloodPass123!',
                'role': 'student'
            }

            try:
                response = client.post(
                    '/api/auth/register/',
                    data=json.dumps(register_data),
                    content_type='application/json'
                )

                end = time.time()

                return {
                    'index': index,
                    'status': response.status_code,
                    'time': end - start,
                    'success': response.status_code == 200
                }
            except Exception as e:
                return {
                    'index': index,
                    'status': 500,
                    'time': time.time() - start,
                    'success': False,
                    'error': str(e)
                }

        with ThreadPoolExecutor(max_workers=15) as executor:
            futures = [executor.submit(flood_registration, i) for i in range(100)]

            for future in futures:
                result = future.result()
                registration_results.append(result)

        successful_registrations = [r for r in registration_results if r['success']]
        success_rate = len(successful_registrations) / len(registration_results)
        avg_registration_time = sum(r['time'] for r in successful_registrations) / len(
            successful_registrations) if successful_registrations else 0

        print(f"🔥 Flood registrations: {len(successful_registrations)}/{len(registration_results)} successful")
        print(f"🔥 Success rate: {success_rate:.2%}")
        print(f"🔥 Average registration time: {avg_registration_time:.3f}s")

        self.assertGreaterEqual(success_rate, 0.80)
        self.assertLess(avg_registration_time, 2.0)

    def test_brute_force_simulation(self):
        """Симуляція brute force атаки через реальні HTTP запити"""
        from django.test import Client
        from django.conf import settings
        import json

        settings.DISABLE_RATE_LIMITING = False

        target_user = self.stress_users[0]
        failed_attempts = 0
        blocked_attempts = 0
        attempt_times = []

        try:
            cache.clear()
            client = Client()

            for i in range(15):
                start_time = time.time()

                response = client.post('/api/auth/login/',
                                       data=json.dumps({
                                           'email': target_user.email,
                                           'password': 'wrong_password'
                                       }),
                                       content_type='application/json',
                                       HTTP_X_FORWARDED_FOR='192.168.1.100'
                                       )

                attempt_time = time.time() - start_time
                attempt_times.append(attempt_time)

                if response.status_code == 400:
                    failed_attempts += 1
                elif response.status_code == 429:
                    blocked_attempts += 1

        finally:
            settings.DISABLE_RATE_LIMITING = getattr(settings, 'DISABLE_RATE_LIMITING', False)
            cache.clear()

        avg_attempt_time = sum(attempt_times) / len(attempt_times) if attempt_times else 0

        print(f"🔥 Brute force simulation:")
        print(f"🔥 Total attempts: {len(attempt_times)}")
        print(f"🔥 Failed attempts (400): {failed_attempts}")
        print(f"🔥 Blocked attempts (429): {blocked_attempts}")
        print(f"🔥 Average attempt time: {avg_attempt_time:.3f}s")

        self.assertGreater(blocked_attempts, 0, "Brute force protection should activate")
        self.assertGreaterEqual(failed_attempts, 3, "Should have failed attempts before blocking")
        self.assertLess(avg_attempt_time, 2.0, "Response time should remain reasonable")
