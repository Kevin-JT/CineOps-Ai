# mypy: ignore-errors
from locust import HttpUser, between, task


class CineOpsLoadTest(HttpUser):
    """
    Load testing suite for the CineOps AI API.
    Simulates user traffic to verify async execution and caching efficiency.
    """

    # Wait between 1 and 3 seconds between requests
    wait_time = between(1.0, 3.0)

    @task(3)
    def check_health(self) -> None:
        """
        Verify the basic health endpoint is responsive under load.
        """
        self.client.get("/api/v1/health", name="Health Check")

    @task(1)
    def check_metrics(self) -> None:
        """
        Verify Prometheus metrics scraping under load.
        """
        self.client.get("/api/v1/metrics", name="Metrics Scrape")

    @task(2)
    def trigger_workflow(self) -> None:
        """
        Trigger the background workflow.
        Since it's backgrounded, the API should return quickly.
        """
        # In a real production scenario, this might be protected by an API key,
        # but for load testing we simulate the background orchestration trigger.
        self.client.post("/api/v1/workflow/trigger", name="Trigger Workflow")
