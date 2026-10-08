import os
import random
import uuid
from locust import HttpUser, task, between

HEADERS = {"Accept": "application/json"}

class ApiUser(HttpUser):
    wait_time = between(1.0, 2.5)

   
    @task(4)
    def get_users(self):
        with self.client.get("/users", headers=HEADERS, name="GET /users", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Error {response.status_code}: {response.text[:120]}")

    @task(3)
    def get_user_emails(self):
        with self.client.get("/users/emails", headers=HEADERS, name="GET /users/emails", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Error {response.status_code}: {response.text[:120]}")

    @task(2)
    def get_over_twenty(self):
        with self.client.get("/users/over-twenty", headers=HEADERS, name="GET /users/over-twenty", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Error {response.status_code}: {response.text[:120]}")

    @task(1)
    def post_users_bulk(self):
        tag = uuid.uuid4().hex[:8]
        payload = {
            "users": [
                {"name": f"User A {tag}", "email": f"a_{tag}@test.com", "birth_date": "1995-05-10"},
                {"name": f"User B {tag}", "email": f"b_{tag}@test.com", "birth_date": "1988-12-01"},
                {"name": f"User C {tag}", "email": f"c_{tag}@test.com", "birth_date": "2001-03-20"},
            ]
        }
        with self.client.post("/users/bulk", json=payload, headers=HEADERS, name="POST /users/bulk", catch_response=True) as response:
            if response.status_code in (200, 201):
                response.success()
            else:
                response.failure(f"Error {response.status_code}: {response.text[:120]}")