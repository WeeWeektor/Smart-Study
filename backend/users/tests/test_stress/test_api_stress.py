# users/tests/test_stress/test_api_stress.py
import threading
import time
import random
from concurrent.futures import ThreadPoolExecutor
from django.test import TransactionTestCase, Client
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
import json

User = get_user_model()


class APIStressTest(TransactionTestCase):
    """Stress тести для API"""

    def setUp(self):
        self.stress_users = []
        for i in range(20):
            user = User.objects.create_user(
                email=f'api_stress_{i}@example.com',
                password='APIStress123!',
                is_verified_email=True,
                is_active=True
            )
            self.stress_users.append(user)

    def test_api_endpoint_bombardment(self):
        """Тест бомбардування API endpoints"""
        endpoints_to_test = [
            ('/api/user/profile/', 'GET'),
            ('/api/user/profile/', 'PATCH'),
            ('/api/auth/logout/', 'POST'),
        ]

        all_results = []

        def api_bombardment(endpoint, method, user):
            client = Client()
            client.force_login(user)

            results = []

            for i in range(20):
                start = time.time()

                if method == 'GET':
                    response = client.get(endpoint)
                elif method == 'PATCH':
                    data = {'user': {'name': f'StressName{i}'}}
                    response = client.patch(
                        endpoint,
                        data=json.dumps(data),
                        content_type='application/json'
                    )
                elif method == 'POST':
                    response = client.post(endpoint)

                end = time.time()

                results.append({
                    'endpoint': endpoint,
                    'method': method,
                    'user': user.email,
                    'iteration': i,
                    'status': response.status_code,
                    'time': end - start,
                    'success': response.status_code in [200, 201, 204]
                })

            return results

        # Одночасні запити до різних endpoints
        with ThreadPoolExecutor(max_workers=15) as executor:
            futures = []

            for endpoint, method in endpoints_to_test:
                for user in self.stress_users[:5]:
                    future = executor.submit(api_bombardment, endpoint, method, user)
                    futures.append(future)

            for future in futures:
                results = future.result()
                all_results.extend(results)

        # Аналіз результатів по endpoints
        for endpoint, method in endpoints_to_test:
            endpoint_results = [r for r in all_results if r['endpoint'] == endpoint and r['method'] == method]
            successful = [r for r in endpoint_results if r['success']]

            success_rate = len(successful) / len(endpoint_results) if endpoint_results else 0
            avg_time = sum(r['time'] for r in successful) / len(successful) if successful else 0

            print(f"🔥 {method} {endpoint}: {len(successful)}/{len(endpoint_results)} successful")
            print(f"🔥 Success rate: {success_rate:.2%}, Avg time: {avg_time:.3f}s")

            self.assertGreaterEqual(success_rate, 0.85)

    def test_file_upload_stress(self):
        """Stress тест завантаження файлів"""
        upload_results = []

        def stress_file_upload(user, file_size_kb):
            client = Client()
            client.force_login(user)

            # Створення файлу заданого розміру
            file_content = b'x' * (file_size_kb * 1024)
            test_file = SimpleUploadedFile(
                f"stress_test_{file_size_kb}kb.jpg",
                file_content,
                content_type="image/jpeg"
            )

            start = time.time()

            try:
                response = client.post(
                    '/api/user/profile/',
                    {'profile_picture': test_file}
                )

                end = time.time()

                return {
                    'user': user.email,
                    'file_size_kb': file_size_kb,
                    'status': response.status_code,
                    'time': end - start,
                    'success': response.status_code in [200, 201]
                }
            except Exception as e:
                return {
                    'user': user.email,
                    'file_size_kb': file_size_kb,
                    'status': 500,
                    'time': time.time() - start,
                    'success': False,
                    'error': str(e)
                }

        # Одночасне завантаження файлів різного розміру
        file_sizes = [10, 50, 100, 200, 500]  # KB

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = []

            for user in self.stress_users[:10]:
                for size in file_sizes:
                    future = executor.submit(stress_file_upload, user, size)
                    futures.append(future)

            for future in futures:
                result = future.result()
                upload_results.append(result)

        successful_uploads = [r for r in upload_results if r['success']]
        success_rate = len(successful_uploads) / len(upload_results) if upload_results else 0
        avg_upload_time = sum(r['time'] for r in successful_uploads) / len(
            successful_uploads) if successful_uploads else 0

        print(f"🔥 File upload stress: {len(successful_uploads)}/{len(upload_results)} successful")
        print(f"🔥 Success rate: {success_rate:.2%}")
        print(f"🔥 Average upload time: {avg_upload_time:.3f}s")

        # Аналіз по розмірах файлів
        for size in file_sizes:
            size_results = [r for r in successful_uploads if r['file_size_kb'] == size]
            if size_results:
                avg_time_for_size = sum(r['time'] for r in size_results) / len(size_results)
                print(f"🔥 {size}KB files: {len(size_results)} successful, avg time: {avg_time_for_size:.3f}s")

        self.assertGreaterEqual(success_rate, 0.80)

    def test_payload_size_stress(self):
        """Stress тест з великими payload"""
        payload_results = []

        def large_payload_test(user, payload_size):
            client = Client()
            client.force_login(user)

            # Створення великого payload
            large_bio = 'x' * payload_size
            data = {
                'profile': {'bio': large_bio}
            }

            start = time.time()

            try:
                response = client.patch(
                    '/api/user/profile/',
                    data=json.dumps(data),
                    content_type='application/json'
                )

                end = time.time()

                return {
                    'user': user.email,
                    'payload_size': payload_size,
                    'status': response.status_code,
                    'time': end - start,
                    'success': response.status_code == 200
                }
            except Exception as e:
                return {
                    'user': user.email,
                    'payload_size': payload_size,
                    'status': 500,
                    'time': time.time() - start,
                    'success': False,
                    'error': str(e)
                }

        # Тестування різних розмірів payload
        payload_sizes = [1000, 5000, 10000, 50000, 100000]  # characters

        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = []

            for user in self.stress_users[:5]:
                for size in payload_sizes:
                    future = executor.submit(large_payload_test, user, size)
                    futures.append(future)

            for future in futures:
                result = future.result()
                payload_results.append(result)

        successful_payloads = [r for r in payload_results if r['success']]
        success_rate = len(successful_payloads) / len(payload_results) if payload_results else 0

        print(f"🔥 Large payload stress: {len(successful_payloads)}/{len(payload_results)} successful")
        print(f"🔥 Success rate: {success_rate:.2%}")

        # Аналіз по розмірах
        for size in payload_sizes:
            size_results = [r for r in successful_payloads if r['payload_size'] == size]
            if size_results:
                avg_time = sum(r['time'] for r in size_results) / len(size_results)
                print(f"🔥 {size} chars payload: {len(size_results)} successful, avg time: {avg_time:.3f}s")

        self.assertGreaterEqual(success_rate, 0.75)
