from locust import HttpUser, between, task

class CensoUser(HttpUser):
    wait_time = between(1, 3)

    @task
    def export_censo_xml(self):
        self.client.get("/census/export-to-xml/")  # Ajusta la URL según tu aplicación

    @task
    def import_censo(self):
        # Agrega la lógica de carga de archivos XML aquí
        pass
