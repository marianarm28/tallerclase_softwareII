import os
import random
import uuid

from locust import HttpUser, task, between

PER_PAGE = int(os.getenv("PER_PAGE", "50"))
MAX_PAGE = int(os.getenv("MAX_PAGE", "500"))

HEADERS = {"Accept": "application/json"}
class ApiUser(HttpUser):
    wait_time = between(1.0, 2.5)

    connection_timeout=10
    network_timeout=30

    def _get_validado(self, path, nombre, campos_extra=()):
        page = random.randint(1, MAX_PAGE)
        with self.client.get(
            f"{path}?page={page}&per_page={PER_PAGE}",
            name=nombre,
            headers=HEADERS,
            catch_response=True,
        ) as response:
            if response.status_code != 200:
                response.failure(f"Fallo en {path} con status {response.status_code}")
                return
            try:
                body = response.json()
            except ValueError:
                response.failure(f"{path} no devolvió JSON válido")
                return
            faltan = [c for c in ("total", "data") + tuple(campos_extra) if c not in body]
            if faltan:
                response.failure(f"Faltan campos en {path}: {faltan}")
            else:
                response.success()

    @task(4)
    def get_users(self):
        self._get_validado("/api/users", "GET /api/users")
            

    @task(3)
    def get_user_emails(self):
                self._get_validado("/api/users/emails", "GET /api/users/emails")


    @task(2)
    def get_over_twenty(self):
        self._get_validado(
            "/api/users/over-twenty",
            "GET /api/users/over-twenty",
            campos_extra=("cutoff_date",),
        )

    @task(1)
    def post_users_bulk(self):
        tag = uuid.uuid4().hex  
        payload = {
            "users": [
                {"name": f"User A {tag[:8]}", "email": f"a_{tag}@test.com", "birth_date": "1995-05-10"},
                {"name": f"User B {tag[:8]}", "email": f"b_{tag}@test.com", "birth_date": "1988-12-01"},
                {"name": f"User C {tag[:8]}", "email": f"c_{tag}@test.com", "birth_date": "2001-03-20"},
            ]
        }
        with self.client.post(
            "/api/users/bulk",
            json=payload,
            name="POST /api/users/bulk",
            headers=HEADERS,
            catch_response=True,
        ) as response:
            
            if response.status_code != 201:
                response.failure(f"Error {response.status_code} al registrar lote: {response.text[:200]}")
                return
            try:
                creados = response.json().get("users", [])
            except ValueError:
                response.failure("El POST no devolvió JSON válido")
                return
            if len(creados) != 3:
                response.failure(f"Se esperaban 3 usuarios creados y llegaron {len(creados)}")
            else:
                response.success()