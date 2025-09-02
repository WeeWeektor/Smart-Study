import io
import json
import threading
import time
from concurrent.futures import ThreadPoolExecutor

from PIL import Image
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TransactionTestCase, Client

from smartStudy_backend import settings
from users.models import CustomUser

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

        with ThreadPoolExecutor(max_workers=15) as executor:
            futures = []

            for endpoint, method in endpoints_to_test:
                for user in self.stress_users[:5]:
                    future = executor.submit(api_bombardment, endpoint, method, user)
                    futures.append(future)

            for future in futures:
                results = future.result()
                all_results.extend(results)

        for endpoint, method in endpoints_to_test:
            endpoint_results = [r for r in all_results if r['endpoint'] == endpoint and r['method'] == method]
            successful = [r for r in endpoint_results if r['success']]

            success_rate = len(successful) / len(endpoint_results) if endpoint_results else 0
            avg_time = sum(r['time'] for r in successful) / len(successful) if successful else 0

            print(f"🔥 {method} {endpoint}: {len(successful)}/{len(endpoint_results)} successful")
            print(f"🔥 Success rate: {success_rate:.2%}, Avg time: {avg_time:.3f}s")

            self.assertGreaterEqual(success_rate, 0.85)

    def test_file_upload_stress(self):
        original_setting = getattr(settings, 'DISABLE_RATE_LIMITING', False)
        settings.DISABLE_RATE_LIMITING = True

        try:
            user = CustomUser.objects.create_user(
                email='stresstest@example.com',
                name='Stress',
                surname='Test',
                password='TestPassword123!',
                role='student',
                is_active=True,
                is_verified_email=True
            )

            self.client.login(email='stresstest@example.com', password='TestPassword123!')

            def create_test_image():
                image = Image.new('RGB', (100, 100), color='red')
                img_io = io.BytesIO()
                image.save(img_io, format='JPEG')
                img_io.seek(0)
                return SimpleUploadedFile(
                    'test.jpg',
                    img_io.getvalue(),
                    content_type='image/jpeg'
                )

            def upload_file():
                try:
                    start_time = time.time()

                    test_file = create_test_image()

                    response = self.client.post(
                        '/api/user/profile/',
                        {'profile_picture': test_file},
                        format='multipart'
                    )

                    elapsed_time = time.time() - start_time

                    return {
                        'success': response.status_code in [200, 201],
                        'status_code': response.status_code,
                        'time': elapsed_time
                    }
                except Exception as e:
                    return {
                        'success': False,
                        'status_code': 500,
                        'time': 0,
                        'error': str(e)
                    }

            threads = []
            results = []
            num_threads = 10

            for i in range(num_threads):
                thread = threading.Thread(target=lambda: results.append(upload_file()))
                threads.append(thread)
                thread.start()

            for thread in threads:
                thread.join()

            successful_uploads = [r for r in results if r['success']]
            success_rate = len(successful_uploads) / len(results)

            print(f"📁 File Upload Stress Test Results:")
            print(f"📁 Total requests: {len(results)}")
            print(f"📁 Successful: {len(successful_uploads)}")
            print(f"📁 Success rate: {success_rate:.2%}")

            if successful_uploads:
                avg_time = sum(r['time'] for r in successful_uploads) / len(successful_uploads)
                print(f"📁 Average response time: {avg_time:.3f}s")

            failed_uploads = [r for r in results if not r['success']]
            if failed_uploads:
                print(f"📁 Failed uploads: {len(failed_uploads)}")
                for i, fail in enumerate(failed_uploads[:3]):
                    print(f"📁 Failure {i + 1}: Status {fail['status_code']}, Error: {fail.get('error', 'N/A')}")

            self.assertGreaterEqual(success_rate, 0.30)

        finally:
            settings.DISABLE_RATE_LIMITING = original_setting

    def test_payload_size_stress(self):
        """Stress тест з великими payload"""
        payload_results = []

        def large_payload_test(user, payload_size):
            client = Client()
            client.force_login(user)

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

        payload_sizes = [1000, 5000, 10000, 50000, 100000]

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

        for size in payload_sizes:
            size_results = [r for r in successful_payloads if r['payload_size'] == size]
            if size_results:
                avg_time = sum(r['time'] for r in size_results) / len(size_results)
                print(f"🔥 {size} chars payload: {len(size_results)} successful, avg time: {avg_time:.3f}s")

        self.assertGreaterEqual(success_rate, 0.75)
