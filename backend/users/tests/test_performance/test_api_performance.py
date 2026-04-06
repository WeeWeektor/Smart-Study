import time
import json
from concurrent.futures import ThreadPoolExecutor
from django.test import TransactionTestCase, Client
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile

User = get_user_model()


class APIPerformanceTest(TransactionTestCase):
    """Тести продуктивності API"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email='api_perf@example.com',
            password='APIPerf123!',
            is_verified_email=True,
            is_active=True
        )
        self.client.force_login(self.user)

    def test_api_response_times(self):
        """Тест часу відповіді API endpoints"""
        endpoints = [
            ('/api/user/profile/', 'GET'),
            ('/api/user/profile/', 'PATCH'),
        ]

        results = {}

        for endpoint, method in endpoints:
            times = []

            for _ in range(10):
                start = time.time()

                if method == 'GET':
                    response = self.client.get(endpoint)
                elif method == 'PATCH':
                    data = {'user': {'name': f'Updated {time.time()}'}}
                    response = self.client.patch(
                        endpoint,
                        data=json.dumps(data),
                        content_type='application/json'
                    )

                end = time.time()
                times.append(end - start)

                self.assertIn(response.status_code, [200, 201, 204])

            avg_time = sum(times) / len(times)
            max_time = max(times)
            min_time = min(times)

            results[f"{method} {endpoint}"] = {
                'avg': avg_time,
                'max': max_time,
                'min': min_time
            }

            print(f"📊 {method} {endpoint} - Avg: {avg_time:.3f}s, Max: {max_time:.3f}s")

            self.assertLess(avg_time, 0.5, f"{method} {endpoint} should respond under 0.5s")

    def test_file_upload_performance(self):
        """Тест продуктивності завантаження файлів"""
        file_sizes = [
            (1024, "1KB"),
            (10240, "10KB"),
            (102400, "100KB"),
            (1048576, "1MB"),
        ]

        for size, label in file_sizes:
            test_file = SimpleUploadedFile(
                f"test_{label}.jpg",
                b"x" * size,
                content_type="image/jpeg"
            )

            start = time.time()
            response = self.client.post(
                '/api/user/profile/',
                {'profile_picture': test_file}
            )
            end = time.time()

            upload_time = end - start
            print(f"📊 File upload {label}: {upload_time:.3f}s")

            if size <= 102400:
                self.assertLess(upload_time, 1.0, f"{label} upload should be under 1s")
            else:
                self.assertLess(upload_time, 3.0, f"{label} upload should be under 3s")

    def test_api_throughput(self):
        """Тест пропускної здатності API"""
        request_count = 100

        start = time.time()

        def make_request():
            response = self.client.get('/api/user/profile/')
            return response.status_code

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(request_count)]
            results = [future.result() for future in futures]

        end = time.time()

        total_time = end - start
        requests_per_second = request_count / total_time
        successful_requests = len([r for r in results if r == 200])

        print(f"📊 API Throughput: {requests_per_second:.1f} req/s, Success: {successful_requests}/{request_count}")

        self.assertEqual(successful_requests, request_count, "All requests should succeed")
        self.assertGreater(requests_per_second, 20, "Should handle at least 20 req/s")

    def test_api_payload_size_performance(self):
        """Тест продуктивності з різними розмірами payload"""
        payloads = [
            {'user': {'name': 'Small'}},
            {'user': {'name': 'Medium', 'bio': 'x' * 1000}},
            {'user': {'name': 'Large', 'bio': 'x' * 10000}},
        ]

        for i, payload in enumerate(payloads):
            payload_size = len(json.dumps(payload))

            start = time.time()
            response = self.client.patch(
                '/api/user/profile/',
                data=json.dumps(payload),
                content_type='application/json'
            )
            end = time.time()

            process_time = end - start
            print(f"📊 Payload {payload_size}B: {process_time:.3f}s")

            self.assertEqual(response.status_code, 200)
            self.assertLess(process_time, 1.0, f"Payload {payload_size}B should process under 1s")
