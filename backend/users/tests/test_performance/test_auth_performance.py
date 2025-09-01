import time
from concurrent.futures import ThreadPoolExecutor
from django.test import TransactionTestCase, Client
from django.contrib.auth import get_user_model
from django.core.cache import cache
import json

User = get_user_model()


class AuthPerformanceTest(TransactionTestCase):
    """Тести продуктивності аутентифікації"""

    def setUp(self):
        self.client = Client()
        cache.clear()

    def test_registration_performance(self):
        """Тест продуктивності реєстрації"""
        registration_times = []

        for i in range(20):
            start = time.time()

            register_data = {
                'name': f'TestUser{i}',
                'surname': f'Surname{i}',
                'email': f'perf_reg_{i}@example.com',
                'password': 'SecurePass123!',
                'role': 'student'
            }

            response = self.client.post(
                '/api/auth/register/',
                data=json.dumps(register_data),
                content_type='application/json'
            )

            end = time.time()
            registration_times.append(end - start)

            self.assertEqual(response.status_code, 200)

        avg_time = sum(registration_times) / len(registration_times)
        max_time = max(registration_times)

        print(f"📊 Registration - Avg: {avg_time:.3f}s, Max: {max_time:.3f}s")

        self.assertLess(avg_time, 0.5, "Average registration time should be under 0.5s")
        self.assertLess(max_time, 2.0, "Max registration time should be under 2s")

    def test_login_performance(self):
        """Тест продуктивності логіну"""
        # Створення тестових користувачів
        users = []
        for i in range(10):
            user = User.objects.create_user(
                email=f'login_perf_{i}@example.com',
                password='LoginPass123!',
                is_verified_email=True
            )
            users.append(user)

        login_times = []

        for user in users:
            start = time.time()

            login_data = {
                'email': user.email,
                'password': 'LoginPass123!'
            }

            response = self.client.post(
                '/api/auth/login/',
                data=json.dumps(login_data),
                content_type='application/json'
            )

            end = time.time()
            login_times.append(end - start)

            self.assertEqual(response.status_code, 200)

            # Логаут для наступного тесту
            self.client.post('/api/auth/logout/')

        avg_time = sum(login_times) / len(login_times)
        print(f"📊 Login performance - Avg: {avg_time:.3f}s")

        self.assertLess(avg_time, 0.3, "Average login time should be under 0.3s")

    def test_concurrent_logins(self):
        """Тест одночасних логінів"""
        # Створення користувачів
        users = []
        for i in range(15):
            user = User.objects.create_user(
                email=f'concurrent_{i}@example.com',
                password='ConcurrentPass123!',
                is_verified_email=True
            )
            users.append(user)

        results = []

        def login_user(user):
            client = Client()
            start = time.time()

            login_data = {
                'email': user.email,
                'password': 'ConcurrentPass123!'
            }

            response = client.post(
                '/api/auth/login/',
                data=json.dumps(login_data),
                content_type='application/json'
            )

            end = time.time()

            results.append({
                'status': response.status_code,
                'time': end - start,
                'user_id': user.id
            })

        # Одночасні логіни
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(login_user, user) for user in users]
            for future in futures:
                future.result()

        successful_logins = [r for r in results if r['status'] == 200]
        avg_time = sum(r['time'] for r in successful_logins) / len(successful_logins)

        print(f"📊 Concurrent logins - Success: {len(successful_logins)}/{len(users)}, Avg: {avg_time:.3f}s")

        self.assertEqual(len(successful_logins), 15, "All concurrent logins should succeed")
        self.assertLess(avg_time, 1.0, "Average concurrent login time should be under 1s")

    def test_password_hashing_performance(self):
        """Тест продуктивності хешування паролів"""
        from django.contrib.auth.hashers import make_password

        passwords = [f'TestPassword{i}123!' for i in range(50)]

        start = time.time()
        hashed_passwords = [make_password(pwd) for pwd in passwords]
        end = time.time()

        total_time = end - start
        avg_time = total_time / len(passwords)

        print(f"📊 Password hashing - Total: {total_time:.3f}s, Avg: {avg_time:.3f}s")

        self.assertLess(avg_time, 0.1, "Average password hashing should be under 0.1s")
        self.assertEqual(len(hashed_passwords), 50, "All passwords should be hashed")

    def test_session_creation_performance(self):
        """Тест продуктивності створення сесій"""
        user = User.objects.create_user(
            email='session_perf@example.com',
            password='SessionPass123!',
            is_verified_email=True
        )

        session_times = []

        for i in range(10):
            client = Client()
            start = time.time()

            # Логін (створює сесію)
            login_data = {
                'email': user.email,
                'password': 'SessionPass123!'
            }

            response = client.post(
                '/api/auth/login/',
                data=json.dumps(login_data),
                content_type='application/json'
            )

            # Доступ до захищеного ресурсу
            profile_response = client.get('/api/user/profile/')

            end = time.time()
            session_times.append(end - start)

            self.assertEqual(response.status_code, 200)
            self.assertEqual(profile_response.status_code, 200)

        avg_time = sum(session_times) / len(session_times)
        print(f"📊 Session creation - Avg: {avg_time:.3f}s")

        self.assertLess(avg_time, 0.4, "Average session creation should be under 0.4s")