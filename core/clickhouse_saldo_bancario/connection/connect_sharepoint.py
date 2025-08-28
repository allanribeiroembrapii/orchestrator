import os
import requests
from msal import PublicClientApplication
from dotenv import load_dotenv
import datetime

load_dotenv()

TENANT_ID = os.getenv("TENANT_ID")
CLIENT_ID = os.getenv("CLIENT_ID")
SHAREPOINT_DOMAIN = os.getenv("SHAREPOINT_DOMAIN")
SHAREPOINT_SITE_NAME = os.getenv("SHAREPOINT_SITE_NAME")
SHAREPOINT_DRIVE_NAME = os.getenv("SHAREPOINT_DRIVE_NAME")
PASTA_DOWNLOAD = os.getenv("PASTA_DOWNLOAD")
AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
SCOPES = ["Files.Read.All", "Sites.Read.All"]


class SharepointClient:
    def __init__(self):
        self.token = self._authenticate()
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/json"
        }

        # 🔽 Pega o site
        self.site = self._get_site()
        self.site_id = self.site["id"]
        self.site_url = f"https://graph.microsoft.com/v1.0/sites/{self.site_id}"

        # 🔽 Drive 'Documentos'
        self.drive_id = self._get_drive_id()


    def _authenticate(self):
        app = PublicClientApplication(CLIENT_ID, authority=AUTHORITY)

        # Tenta usar cache
        accounts = app.get_accounts()
        if accounts:
            result = app.acquire_token_silent(SCOPES, account=accounts[0])
        else:
            result = app.acquire_token_interactive(SCOPES)

        if "access_token" not in result:
            raise Exception(f"Erro ao obter token: {result.get('error_description')}")
        return result["access_token"]

    def _get_site(self):
        url = f"https://graph.microsoft.com/v1.0/sites/{SHAREPOINT_DOMAIN}:/sites/{SHAREPOINT_SITE_NAME}"
        res = requests.get(url, headers=self.headers)
        res.raise_for_status()
        return res.json()  # Retorna tudo

    def _get_site_id(self):
        url = f"https://graph.microsoft.com/v1.0/sites/{SHAREPOINT_DOMAIN}:/sites/{SHAREPOINT_SITE_NAME}"
        res = requests.get(url, headers=self.headers)
        res.raise_for_status()
        return res.json()["id"]

    def _get_drive_id(self):
        url = f"{self.site_url}/drives"
        res = requests.get(url, headers=self.headers)
        res.raise_for_status()

        drives = res.json().get("value", [])
        for d in drives:
            print(f" - {d['name']}")

        # 🔽 Selecionar exatamente o drive chamado "Documentos"
        for d in drives:
            if d["name"].lower() == "documentos":
                return d["id"]

        raise Exception("Drive 'Documentos' não encontrado")


    def list_files(self, folder_path=""):
        url = f"https://graph.microsoft.com/v1.0/drives/{self.drive_id}/root:/{folder_path}:/children"
        res = requests.get(url, headers=self.headers)
        res.raise_for_status()
        return res.json()["value"]

    def download_file(self, file_path, output_path):
        url = f"https://graph.microsoft.com/v1.0/drives/{self.drive_id}/root:/{file_path}:/content"
        res = requests.get(url, headers=self.headers, stream=True)
        res.raise_for_status()
        with open(output_path, "wb") as f:
            for chunk in res.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"✅ Arquivo baixado para: {output_path}")

    def upload_file(self, local_file_path, target_file_path):
        with open(local_file_path, "rb") as f:
            file_data = f.read()
        url = f"https://graph.microsoft.com/v1.0/drives/{self.drive_id}/root:/{target_file_path}:/content"
        res = requests.put(url, headers=self.headers, data=file_data)
        res.raise_for_status()
        print(f"✅ Arquivo enviado para: {target_file_path}")
    
    def download_latest_file(self, folder_path, output_dir="."):
        """
        Baixa o último arquivo modificado dentro da pasta especificada.
        Ex: folder_path="DWPII/srinfo"
        """
        url = f"https://graph.microsoft.com/v1.0/drives/{self.drive_id}/root:/{folder_path}:/children"
        res = requests.get(url, headers=self.headers)
        res.raise_for_status()

        files = res.json()["value"]
        files = [f for f in files if "file" in f]  # Ignora subpastas

        if not files:
            raise Exception("Nenhum arquivo encontrado na pasta.")

        latest_file = max(files, key=lambda x: x["lastModifiedDateTime"])
        file_name = latest_file["name"]
        download_url = f"https://graph.microsoft.com/v1.0/drives/{self.drive_id}/items/{latest_file['id']}/content"

        res = requests.get(download_url, headers=self.headers, stream=True)
        res.raise_for_status()

        output_path = os.path.join(output_dir, file_name)
        with open(output_path, "wb") as f:
            for chunk in res.iter_content(chunk_size=8192):
                f.write(chunk)

    def upload_file_to_folder(self, local_file_path, folder_path):
        file_name = os.path.basename(local_file_path)
        with open(local_file_path, "rb") as f:
            file_data = f.read()

        if folder_path:
            upload_path = f"{folder_path}/{file_name}"
        else:
            upload_path = file_name

        url = f"https://graph.microsoft.com/v1.0/drives/{self.drive_id}/root:/{upload_path}:/content"
        res = requests.put(url, headers=self.headers, data=file_data)

        if not res.ok:
            print(f"❌ Erro ao enviar: {res.status_code} - {res.text}")
        res.raise_for_status()
        print(f"✅ Enviado para: /{upload_path}")




if __name__ == "__main__":
    sp = SharepointClient()
    files = sp.list_files("dw_pii")
    for f in files:
        print("-", f["name"])
    sp.upload_file_to_folder("orcado_realizado.xlsx", "")
    # Baixar o último arquivo da pasta DWPII
    # sp.download_latest_file("DWPII/srinfo", output_dir=PASTA_DOWNLOAD)