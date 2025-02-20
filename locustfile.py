from locust import HttpUser, task

class WalletUser(HttpUser):
    @task
    def deposit(self):
        self.client.post("/wallets/2f25e341-b102-49c1-93fe-60fefdd20c8c/operation", json={
            "operationType": "deposit",
            "amount": 1000.00
        })


