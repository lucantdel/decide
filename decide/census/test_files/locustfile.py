from locust import HttpUser, between, task
import os

class CensoUser(HttpUser):
    wait_time = between(1, 3)

    '''def on_start(self):
        # Obtener el token CSRF al inicio
        response = self.client.get("/census/")  # Cambia a una ruta que no requiera CSRF para obtener el token
        csrf_token = response.cookies.get('csrftoken', default=None)
        self.headers = {'X-CSRFToken': csrf_token}'''

    @task
    def export_censo_xml(self):
        response = self.client.get("/census/export-to-xml/")
        assert response.status_code == 200, f"Failed to export census XML. Status code: {response.status_code}"

    '''@task
    def import_censo_xml(self):
        # Realiza una solicitud GET para obtener el token CSRF y configurar las cookies
        response_get = self.client.get("/census/")
        
        # Asegúrate de que la solicitud GET fue exitosa (código 200)
        assert response_get.status_code == 200

        file_path = os.path.abspath(os.path.expanduser("~/Descargas/import_test_data1.xml"))
        print(file_path)

        # Realiza la solicitud POST con el token CSRF y otros datos
        response_post = self.client.post(
            "/census/import-from-xml/",
            files={"xml_file": ("import_test_data1.xml", open(file_path, "rb"))},
            headers={"Referer": "/census/import-from-xml/"},  # Asegúrate de incluir el encabezado Referer
        )
        
        # Asegúrate de que la solicitud POST fue exitosa (código 200)
        assert response_post.status_code == 200'''
