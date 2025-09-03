import time
from concurrent.futures import ThreadPoolExecutor
from django.test import TransactionTestCase, Client
from django.contrib.auth import get_user_model
from django.core.cache import cache
import json

from smartStudy_backend import settings
from users.models import CustomUser

User = get_user_model()


class AuthPerformanceTest(TransactionTestCase):
    """Тести продуктивності аутентифікації"""

    def setUp(self):
        self.client = Client()
        cache.clear()

    def test_registration_performance(self):
        """Тест продуктивності реєстрації"""
        from django.conf import settings

        original_setting = getattr(settings, 'DISABLE_RATE_LIMITING', False)
        settings.DISABLE_RATE_LIMITING = True

        try:
            registration_times = []

            for i in range(20):
                start_time = time.time()

                register_data = {
                    'name': 'Test',
                    'surname': f'User{i}',
                    'email': f'perf_reg_{i}@example.com',
                    'password': 'SecurePass123!',
                    'role': 'student'
                }

                response = self.client.post('/api/auth/register/',
                                            data=json.dumps(register_data),
                                            content_type='application/json')

                end_time = time.time()
                registration_times.append(end_time - start_time)

                self.assertEqual(response.status_code, 200)

            avg_time = sum(registration_times) / len(registration_times)
            max_time = max(registration_times)

            print(f"📝 Registration - Avg: {avg_time:.3f}s, Max: {max_time:.3f}s")

            self.assertLess(avg_time, 0.8, "Average registration time should be under 0.8s")
            self.assertLess(max_time, 1.5, "Max registration time should be under 1.5s")

        finally:
            settings.DISABLE_RATE_LIMITING = original_setting
            cache.clear()
            try:
                User.objects.filter(email__startswith='perf_reg_').delete()
            except:
                pass

    def test_login_performance(self):
        """Test login performance with valid credentials"""
        from django.conf import settings

        original_setting = getattr(settings, 'DISABLE_RATE_LIMITING', False)
        settings.DISABLE_RATE_LIMITING = True

        try:
            cache.clear()

            user = User.objects.create_user(
                name='Test',
                surname='User',
                email='testlogin@example.com',
                password='TestPassword123!',
                role='student',
                is_active=True,
                is_verified_email=True
            )

            login_times = []
            client = Client()

            for i in range(10):
                login_data = {
                    'email': 'testlogin@example.com',
                    'password': 'TestPassword123!'
                }

                start_time = time.time()
                response = client.post('/api/auth/login/',
                                       data=json.dumps(login_data),
                                       content_type='application/json')
                end_time = time.time()

                client.post('/api/auth/logout/')

                login_times.append(end_time - start_time)

                self.assertEqual(response.status_code, 200,
                                 f"Login failed on attempt {i + 1}: {response.content}")

            avg_time = sum(login_times) / len(login_times)
            max_time = max(login_times)

            print(f"🔐 Login - Avg: {avg_time:.3f}s, Max: {max_time:.3f}s")

            self.assertLess(avg_time, 0.7, "Average login time should be under 0.7s")
            self.assertLess(max_time, 1.2, "Max login time should be under 1.2s")

        finally:
            settings.DISABLE_RATE_LIMITING = original_setting
            cache.clear()
            try:
                User.objects.filter(email='testlogin@example.com').delete()
            except:
                pass

    def test_concurrent_logins(self):
        """Тест конкурентних логінів з валідними користувачами"""
        from django.conf import settings

        original_setting = getattr(settings, 'DISABLE_RATE_LIMITING', False)
        settings.DISABLE_RATE_LIMITING = True

        try:
            cache.clear()

            test_users = []
            for i in range(10):
                user = User.objects.create_user(
                    name=f'TestUser{i}',
                    surname=f'Surname{i}',
                    email=f'concurrent_test_{i}@example.com',
                    password='testpass123',
                    role='student',
                    is_active=True,
                    is_verified_email=True
                )
                test_users.append(user)

            def login_user(user_data):
                client = Client()
                start_time = time.time()

                response = client.post('/api/auth/login/',
                                       json.dumps({
                                           'email': user_data['email'],
                                           'password': user_data['password']
                                       }),
                                       content_type='application/json'
                                       )

                end_time = time.time()

                return {
                    'user_id': user_data['id'],
                    'status_code': response.status_code,
                    'time': end_time - start_time,
                    'success': response.status_code == 200
                }

            login_data = [
                {
                    'id': user.id,
                    'email': user.email,
                    'password': 'testpass123'
                }
                for user in test_users
            ]

            start_time = time.time()

            with ThreadPoolExecutor(max_workers=5) as executor:
                results = list(executor.map(login_user, login_data))

            total_time = time.time() - start_time

            successful_logins = [r for r in results if r['success']]
            failed_logins = [r for r in results if not r['success']]

            print(f"🚀 Concurrent login test:")
            print(f"🚀 Total requests: {len(results)}")
            print(f"🚀 Successful logins: {len(successful_logins)}")
            print(f"🚀 Failed logins: {len(failed_logins)}")
            print(f"🚀 Total time: {total_time:.3f}s")

            if successful_logins:
                avg_time = sum(r['time'] for r in successful_logins) / len(successful_logins)
                max_time = max(r['time'] for r in successful_logins)
                min_time = min(r['time'] for r in successful_logins)

                print(f"🚀 Average login time: {avg_time:.3f}s")
                print(f"🚀 Min/Max login time: {min_time:.3f}s / {max_time:.3f}s")

                self.assertGreater(len(successful_logins), 0, "Should have successful logins")
                self.assertLess(avg_time, 2.0, "Average login time should be under 2 seconds")
                self.assertLess(max_time, 5.0, "Max login time should be under 5 seconds")

                success_rate = len(successful_logins) / len(results)
                self.assertGreater(success_rate, 0.8, "Success rate should be above 80%")
            else:
                self.fail("No successful logins - check test setup or rate limiting")

            expected_sequential_time = len(test_users) * 0.5
            self.assertLess(total_time, expected_sequential_time,
                            "Concurrent processing should be faster than sequential")

        finally:
            settings.DISABLE_RATE_LIMITING = original_setting
            cache.clear()

            for user in test_users:
                try:
                    user.delete()
                except:
                    pass

    def test_password_hashing_performance(self):
        original_setting = getattr(settings, 'DISABLE_RATE_LIMITING', False)
        settings.DISABLE_RATE_LIMITING = True

        try:
            password = "TestPassword123!"
            times = []

            for i in range(10):
                start_time = time.time()
                user = CustomUser.objects.create_user(
                    email=f'perftest{i}@example.com',
                    name='Performance',
                    surname='Test',
                    password=password,
                    role='student'
                )
                end_time = time.time()
                times.append(end_time - start_time)
                user.delete()

            avg_time = sum(times) / len(times)
            self.assertLess(avg_time, 0.6, "Average password hashing should be under 0.6s")

        finally:
            settings.DISABLE_RATE_LIMITING = original_setting

    def test_session_creation_performance(self):
        """Test session creation performance"""
        from django.conf import settings

        original_setting = getattr(settings, 'DISABLE_RATE_LIMITING', False)
        settings.DISABLE_RATE_LIMITING = True

        try:
            test_user = User.objects.create_user(
                name='SessionTest',
                surname='User',
                email='sessiontest@example.com',
                password='TestPass123!',
                role='student',
                is_active=True,
                is_verified_email=True
            )

            session_times = []

            for i in range(10):
                self.client = Client()

                start = time.time()

                login_data = {
                    'email': 'sessiontest@example.com',
                    'password': 'TestPass123!'
                }

                response = self.client.post('/api/auth/login/',
                                            data=json.dumps(login_data),
                                            content_type='application/json')

                end = time.time()
                session_times.append(end - start)

                self.assertEqual(response.status_code, 200)

            avg_time = sum(session_times) / len(session_times)
            max_time = max(session_times)

            print(f"🔑 Session Creation - Avg: {avg_time:.3f}s, Max: {max_time:.3f}s")

            self.assertLess(avg_time, 0.7, "Average session creation should be under 0.7s")
            self.assertLess(max_time, 1.0, "Max session creation should be under 1.0s")

        finally:
            settings.DISABLE_RATE_LIMITING = original_setting
            cache.clear()
            try:
                User.objects.filter(email='sessiontest@example.com').delete()
            except:
                pass
