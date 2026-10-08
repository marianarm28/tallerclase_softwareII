import uuid
from locust import HttpUser, task, between

class ApiUser(HttpUser):
    wait_time = between(1.0, 2.5)

    @task(4)
    def get_users(self):
        with self.client.get("/users", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Fallo en /users con status {response.status_code}")


    @task(3)
    def get_user_emails(self):
        with self.client.get("/users/emails", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Fallo en /users/emails con status {response.status_code}")

    @task(2)
    def get_over_twenty(self):
        with self.client.get("/users/over-twenty", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Fallo en /users/over-twenty con status {response.status_code}")

    @task(1)
    def post_users_bulk(self):
        # UUID para garantizar correos únicos bajo concurrencia y evitar el error 422
        tag = uuid.uuid4().hex[:8]
        payload = {
            "users": [
                {"name": f"User A {tag}", "email": f"a_{tag}@test.com", "birth_date": "1995-05-10"},
                {"name": f"User B {tag}", "email": f"b_{tag}@test.com", "birth_date": "1988-12-01"},
                {"name": f"User C {tag}", "email": f"c_{tag}@test.com", "birth_date": "2001-03-20"}
            ]
        }
        with self.client.post("/users/bulk", json=payload, catch_response=True) as response:
            if response.status_code in [200, 201]:
                response.success()
            else:
                response.failure(f"Error {response.status_code} al registrar lote: {response.text}")