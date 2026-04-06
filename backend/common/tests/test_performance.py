import time
import threading
from django.test import TestCase
from django.http import HttpRequest
from common.utils.language_utils import get_language_from_request


class TestPerformanceStress(TestCase):
    """Стрес-тести продуктивності"""

    def test_high_load_language_detection(self):
        """Тест під високим навантаженням"""
        start_time = time.time()

        for _ in range(1000):
            request = HttpRequest()
            request.META['HTTP_ACCEPT_LANGUAGE'] = 'en-US,en;q=0.9,uk;q=0.8'
            result = get_language_from_request(request)
            self.assertEqual(result, 'en')

        total_time = time.time() - start_time
        self.assertLess(total_time, 0.5)

    def test_concurrent_safety(self):
        """Тест thread safety"""
        results = []

        def worker():
            request = HttpRequest()
            request.META['HTTP_X_LANGUAGE'] = 'uk'
            result = get_language_from_request(request)
            results.append(result)

        threads = [threading.Thread(target=worker) for _ in range(50)]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        self.assertEqual(len(results), 50)
        self.assertTrue(all(r == 'uk' for r in results))
