from locust import HttpUser, task, between


class MedScribeUser(HttpUser):
    wait_time = between(1, 3)
    host = "http://localhost:8000"

    def on_start(self):
        self.token = "test_token"
        self.headers = {"Authorization": f"Bearer {self.token}"}

    @task(3)
    def health_check(self):
        self.client.get("/health")

    @task(5)
    def list_patients(self):
        self.client.get("/patients", headers=self.headers)

    @task(2)
    def search_patients(self):
        self.client.get("/patients/search?q=test", headers=self.headers)

    @task(3)
    def dashboard_stats(self):
        self.client.get("/dashboard/stats", headers=self.headers)

    @task(2)
    def search(self):
        self.client.get("/search?q=headache", headers=self.headers)

    @task(1)
    def list_tags(self):
        self.client.get("/tags", headers=self.headers)
