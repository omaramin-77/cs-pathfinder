import time
import pytest
import random
import string
import sys
import os
from datetime import datetime, timedelta

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app
from DB import get_db_connection

# Constants for performance testing
NUM_CONCURRENT_USERS = 100
NUM_REQUESTS_PER_USER = 5

# Helper function to generate random strings
def random_string(length=10):
    """Generate a random string of fixed length"""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

# Performance test for database operations
@pytest.mark.performance
def test_database_read_performance():
    """Test the performance of database read operations"""
    start_time = time.time()
    
    with app.app_context():
        conn = get_db_connection()
        for _ in range(100):  # Perform 100 reads
            conn.execute('SELECT * FROM users LIMIT 10').fetchall()
        conn.close()
    
    elapsed = time.time() - start_time
    print(f"\nDatabase read performance: {elapsed:.4f} seconds for 100 reads")
    assert elapsed < 1.0  # Should complete in under 1 second

# Performance test for user registration
@pytest.mark.performance
def test_user_registration_performance():
    """Test the performance of user registration"""
    test_emails = [f"perf_test_{i}@test.com" for i in range(NUM_CONCURRENT_USERS)]
    
    start_time = time.time()
    
    with app.test_client() as client:
        for email in test_emails:
            # Simulate concurrent user registrations
            for _ in range(NUM_REQUESTS_PER_USER):
                response = client.post('/signup', data={
                    'email': email,
                    'password': 'Testpass123!'
                }, follow_redirects=True)
                assert response.status_code == 200
    
    elapsed = time.time() - start_time
    total_requests = NUM_CONCURRENT_USERS * NUM_REQUESTS_PER_USER
    req_per_sec = total_requests / elapsed if elapsed > 0 else 0
    
    print(f"\nUser registration performance: {elapsed:.4f} seconds for {total_requests} requests")
    print(f"Requests per second: {req_per_sec:.2f}")
    
    # Cleanup test users
    with app.app_context():
        conn = get_db_connection()
        for email in test_emails:
            conn.execute('DELETE FROM users WHERE email = ?', (email,))
        conn.commit()
        conn.close()

# Performance test for concurrent user sessions
@pytest.mark.performance
def test_concurrent_user_sessions():
    """Test performance with multiple concurrent user sessions"""
    test_users = [
        (f"concurrent_{i}@test.com", f"pass{i}Test!") 
        for i in range(NUM_CONCURRENT_USERS)
    ]
    
    # Register test users
    with app.test_client() as client:
        for email, password in test_users:
            client.post('/signup', data={
                'email': email,
                'password': password
            }, follow_redirects=True)
    
    # Test concurrent logins and dashboard access
    start_time = time.time()
    
    def simulate_user_session(email, password):
        with app.test_client() as client:
            # Login
            client.post('/login', data={
                'email': email,
                'password': password
            }, follow_redirects=True)
            
            # Access home page
            response = client.get('/', follow_redirects=True)
            assert response.status_code == 200
            
            # Access results page
            response = client.get('/results', follow_redirects=True)
            assert response.status_code == 200
    
    # Simulate concurrent users
    import threading
    threads = []
    for email, password in test_users:
        t = threading.Thread(target=simulate_user_session, args=(email, password))
        threads.append(t)
        t.start()
    
    # Wait for all threads to complete
    for t in threads:
        t.join()
    
    elapsed = time.time() - start_time
    print(f"\nConcurrent user sessions: {elapsed:.4f} seconds for {len(test_users)} users")
    
    # Cleanup
    with app.app_context():
        conn = get_db_connection()
        for email, _ in test_users:
            conn.execute('DELETE FROM users WHERE email = ?', (email,))
        conn.commit()
        conn.close()

# Performance test for AI helper functions
@pytest.mark.performance
def test_ai_processing_performance():
    """Test the performance of AI processing functions"""
    from ai_helper import build_prompt, get_available_fields
    
    # Generate test data
    test_answers = {
        str(i): {"question": f"Question {i}", "answer": f"Answer {i}" * 10}
        for i in range(20)  # 20 test questions/answers
    }
    
    # Test build_prompt performance
    start_time = time.time()
    for _ in range(10):  # Run multiple times for more accurate measurement
        build_prompt(test_answers, get_available_fields())
    elapsed = (time.time() - start_time) / 10  # Average time per call
    
    print(f"\nAI prompt building performance: {elapsed:.4f} seconds per call")
    assert elapsed < 0.1  # Should be very fast

