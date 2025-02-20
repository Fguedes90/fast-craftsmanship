from locust import HttpUser, task, between, events

class BackendUser(HttpUser):
    wait_time = between(1, 5)
    token = None
    
    def on_start(self):
        """Login at the start of each user session"""
        response = self.client.post(
            "/api/v1/login/access-token",
            data={
                "grant_type": "password",
                "username": "admin@fastapi.com",
                "password": "string123456",
                "scope": "",
                "client_id": "string",
                "client_secret": "string"
            },
            headers={
                'Content-Type': 'application/x-www-form-urlencoded',
                'accept': 'application/json'
            },
            name="login"
        )
        if response.status_code == 200:
            self.token = response.json()["access_token"]

    @task(1)
    def openapi(self):
        self.client.get("/api/v1/openapi.json", name="openapi")

    @task(2)
    def metrics(self):
        self.client.get("http://localhost:8000/metrics", name="metrics", verify=False)

    @task(3)
    def get_users(self):
        """Test the users endpoint"""
        if self.token:
            self.client.get(
                "/api/v1/users",
                headers={"Authorization": f"Bearer {self.token}"} if self.token else {},
                name="get_users"
            )

    @task(4)
    def get_current_user(self):
        """Test the current user endpoint"""
        if self.token:
            self.client.get(
                "/api/v1/users/me",
                headers={"Authorization": f"Bearer {self.token}"} if self.token else {},
                name="get_current_user"
            )

    def on_stop(self):
        """Clean up after the user session ends"""
        self.token = None

