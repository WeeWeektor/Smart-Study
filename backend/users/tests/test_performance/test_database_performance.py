import time
from django.test import TransactionTestCase
from django.contrib.auth import get_user_model

User = get_user_model()


class DatabasePerformanceTest(TransactionTestCase):
    """Тести продуктивності бази даних"""

    def test_query_performance(self):
        """Тест продуктивності запитів"""
        # Створення тестових даних
        users = [
            User(
                email=f'query_test_{i}@example.com',
                password='hashedpass',
                name=f'User{i}',
                role='student' if i % 2 == 0 else 'teacher'
            ) for i in range(1000)
        ]

        start = time.time()
        User.objects.bulk_create(users, batch_size=100)
        creation_time = time.time() - start

        print(f"📊 1000 users creation: {creation_time:.3f}s")
        self.assertLess(creation_time, 5.0, "Bulk creation should be under 5s")

        # Тест різних типів запитів
        queries = [
            ('Simple filter', lambda: User.objects.filter(role='student').count()),
            ('Complex filter', lambda: User.objects.filter(
                role='teacher',
                email__icontains='query_test'
            ).count()),
            ('Ordering', lambda: list(User.objects.filter(
                email__startswith='query_test'
            ).order_by('email')[:10])),
            ('Aggregation', lambda: User.objects.filter(
                email__startswith='query_test'
            ).values('role').distinct().count()),
        ]

        for query_name, query_func in queries:
            start = time.time()
            result = query_func()
            end = time.time()

            query_time = end - start
            print(f"📊 {query_name}: {query_time:.3f}s")

            self.assertLess(query_time, 1.0, f"{query_name} should execute under 1s")

    def test_connection_pooling_performance(self):
        """Тест продуктивності пулу з'єднань"""
        times = []

        for i in range(20):
            start = time.time()

            # Простий запит
            User.objects.filter(email='nonexistent@example.com').exists()

            end = time.time()
            times.append(end - start)

        avg_time = sum(times) / len(times)
        print(f"📊 Connection pooling - Avg: {avg_time:.4f}s")

        self.assertLess(avg_time, 0.01, "Database connections should be very fast")

    def test_index_effectiveness(self):
        """Тест ефективності індексів"""
        # Створення даних для тестування індексів
        User.objects.bulk_create([
            User(
                email=f'index_test_{i}@domain{i % 10}.com',
                password='pass',
                name=f'IndexUser{i}'
            ) for i in range(5000)
        ], batch_size=500)

        # Тест запитів що повинні використовувати індекси
        indexed_queries = [
            ('Email lookup', lambda: User.objects.filter(
                email='index_test_100@domain0.com'
            ).exists()),
            ('Email prefix', lambda: User.objects.filter(
                email__startswith='index_test_1'
            ).count()),
        ]

        for query_name, query_func in indexed_queries:
            start = time.time()
            result = query_func()
            end = time.time()

            query_time = end - start
            print(f"📊 {query_name} (indexed): {query_time:.4f}s")

            # Індексовані запити повинні бути дуже швидкими
            self.assertLess(query_time, 0.1, f"{query_name} should use index efficiently")