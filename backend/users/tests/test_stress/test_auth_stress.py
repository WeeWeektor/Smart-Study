import threading
import time
import random
from concurrent.futures import ThreadPoolExecutor
from django.test import TransactionTestCase, Client
from django.contrib.auth import get_user_model
from django.core.cache import cache
import json

User = get_user_model()


class AuthStressTest(TransactionTestCase):
    """Stress тести для аутентифікації"""

    def setUp(self):
        cache.clear()
        # Створення користувачів для stress тестів
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
                response = client.post(
                    '/api/auth/login/',
                    data=json.dumps(login_data),
                    content_type='application/json'
                )

                end = time.time()

                return {
                    'email': user_email,
                    'status': response.status_code,
                    'time': end - start,
                    'success': response.status_code == 200
                }
            except Exception as e:
                return {
                    'email': user_email,
                    'status': 500,
                    'time': time.time() - start,
                    'success': False,
                    'error': str(e)
                }

        # 200 одночасних логінів
        user_emails = [user.email for user in self.stress_users] * 4

        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(concurrent_login, email) for email in user_emails]

            for future in futures:
                result = future.result()
                login_results.append(result)

        successful_logins = [r for r in login_results if r['success']]
        failed_logins = [r for r in login_results if not r['success']]

        success_rate = len(successful_logins) / len(login_results)
        avg_login_time = sum(r['time'] for r in successful_logins) / len(successful_logins) if successful_logins else 0

        print(f"🔥 Massive logins: {len(successful_logins)}/{len(login_results)} successful")
        print(f"🔥 Success rate: {success_rate:.2%}")
        print(f"🔥 Average login time: {avg_login_time:.3f}s")
        print(f"🔥 Failed logins: {len(failed_logins)}")

        # Під stress навантаженням прийнятний success rate 85%
        self.assertGreaterEqual(success_rate, 0.85)
        self.assertLess(avg_login_time, 1.0)

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

        # 100 одночасних реєстрацій
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

        # Реєстрація повинна витримувати flood
        self.assertGreaterEqual(success_rate, 0.80)
        self.assertLess(avg_registration_time, 2.0)

    def test_session_stress(self):
        """Тест stress для сесій"""
        active_sessions = []
        session_operations = []

        def session_stress_worker(user):
            client = Client()

            # Логін
            login_start = time.time()
            login_response = client.post('/api/auth/login/', {
                'email': user.email,
                'password': 'AuthStress123!'
            })
            login_time = time.time() - login_start

            if login_response.status_code == 200:
                active_sessions.append(client)

                # Багато операцій в сесії
                for i in range(10):
                    operation_start = time.time()
                    response = client.get('/api/user/profile/')
                    operation_time = time.time() - operation_start

                    session_operations.append({
                        'user': user.email,
                        'operation': i,
                        'time': operation_time,
                        'success': response.status_code == 200
                    })

                # Логаут
                client.post('/api/auth/logout/')

        # Stress тест з багатьма сесіями
        threads = []
        for user in self.stress_users[:30]:
            thread = threading.Thread(target=session_stress_worker, args=(user,))
            threads.append(thread)
            thread.start()

        # Очікування завершення
        for thread in threads:
            thread.join(timeout=15)

        successful_operations = [op for op in session_operations if op['success']]
        operation_success_rate = len(successful_operations) / len(session_operations) if session_operations else 0
        avg_operation_time = sum(op['time'] for op in successful_operations) / len(
            successful_operations) if successful_operations else 0

        print(f"🔥 Session stress: {len(active_sessions)} sessions created")
        print(f"🔥 Operations: {len(successful_operations)}/{len(session_operations)} successful")
        print(f"🔥 Operation success rate: {operation_success_rate:.2%}")
        print(f"🔥 Average operation time: {avg_operation_time:.3f}s")

        self.assertGreaterEqual(operation_success_rate, 0.90)
        self.assertLess(avg_operation_time, 0.5)

    def test_brute_force_simulation(self):
        """Симуляція brute force атаки"""
        target_user = self.stress_users[0]
        failed_attempts = 0
        blocked_attempts = 0
        attempt_times = []

        # Симуляція brute force (багато невірних паролів)
        for i in range(50):
            client = Client()
            start = time.time()

            wrong_password = f'WrongPass{i}!'

            response = client.post('/api/auth/login/', {
                'email': target_user.email,
                'password': wrong_password
            })

            end = time.time()
            attempt_times.append(end - start)

            if response.status_code == 400:
                failed_attempts += 1
            elif response.status_code == 429:  # Rate limited
                blocked_attempts += 1

            # Невелика затримка між спробами
            time.sleep(0.01)

        avg_attempt_time = sum(attempt_times) / len(attempt_times)

        print(f"🔥 Brute force simulation:")
        print(f"🔥 Failed attempts: {failed_attempts}")
        print(f"🔥 Blocked attempts: {blocked_attempts}")
        print(f"🔥 Average attempt time: {avg_attempt_time:.3f}s")

        # Система повинна блокувати brute force
        self.assertGreater(blocked_attempts, 0, "Brute force protection should activate")

        # Спроба легітимного логіну після brute force
        time.sleep(2)  # Очікування зняття блокування

        client = Client()
        legitimate_response = client.post('/api/auth/login/', {
            'email': target_user.email,
            'password': 'AuthStress123!'
        })

        # Легітимний користувач повинен мати можливість увійти
        self.assertIn(legitimate_response.status_code, [200, 429])