from urllib import response
from office365.sharepoint.client_context import ClientContext
from office365.runtime.auth.user_credential import UserCredential
from office365.sharepoint.files.file import File
import datetime
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

USERNAME = os.getenv('sharepoint_email')
PASSWORD = os.getenv('sharepoint_password')

class SharePoint:
    def _auth(self, sharepoint_site):
        conn = ClientContext(sharepoint_site).with_credentials(
            UserCredential(
                USERNAME,
                PASSWORD
            )
        )
        return conn

    def _get_files_list(self, sharepoint_site, sharepoint_doc, folder_name):
        conn = self._auth(sharepoint_site)
        target_folder_url = f'{sharepoint_doc}/{folder_name}'
        root_folder = conn.web.get_folder_by_server_relative_url(target_folder_url)
        root_folder.expand(["Files", "Folders"]).get().execute_query()
        return root_folder.files

    def get_folder_list(self, sharepoint_site, sharepoint_doc, folder_name):
        conn = self._auth(sharepoint_site)
        target_folder_url = f'{sharepoint_doc}/{folder_name}'
        root_folder = conn.web.get_folder_by_server_relative_url(target_folder_url)
        root_folder.expand(["Folders"]).get().execute_query()
        return root_folder.folders

    def download_file(self, sharepoint_site, sharepoint_site_name, sharepoint_doc, file_name, folder_name):
        conn = self._auth(sharepoint_site)
        file_url = f'/sites/{sharepoint_site_name}/{sharepoint_doc}/{folder_name}/{file_name}'
        # print(f'Debug: URL do arquivo -> {file_url}')
        file = File.open_binary(conn, file_url)
        return file.content


    def download_latest_file(self, sharepoint_site, sharepoint_site_name, sharepoint_doc, folder_name):
        date_format = "%Y-%m-%dT%H:%M:%SZ"
        files_list = self._get_files_list(sharepoint_site, sharepoint_doc, folder_name)
        file_dict = {}
        for file in files_list:
            dt_obj = datetime.datetime.strptime(file.time_last_modified, date_format)
            file_dict[file.name] = dt_obj
        # sort dict object to get the latest file
        file_dict_sorted = {key: value for key, value in sorted(file_dict.items(), key=lambda item: item[1], reverse=True)}    
        latest_file_name = next(iter(file_dict_sorted))
        content = self.download_file(sharepoint_site, sharepoint_site_name, sharepoint_doc, latest_file_name, folder_name)
        return latest_file_name, content

    def upload_file(self, folder_name, sharepoint_site, sharepoint_site_name, sharepoint_doc, file_name, content):
        conn = self._auth(sharepoint_site)
        target_folder_url = f'/sites/{sharepoint_site_name}/{sharepoint_doc}/{folder_name}'
        target_folder = conn.web.get_folder_by_server_relative_path(target_folder_url)
        response = target_folder.upload_file(file_name, content).execute_query()
        return response

    def upload_file_in_chunks(self, sharepoint_site, sharepoint_site_name, sharepoint_doc, file_path, folder_name, chunk_size, chunk_uploaded=None, **kwargs):
        conn = self._auth(sharepoint_site)
        target_folder_url = f'/sites/{sharepoint_site_name}/{sharepoint_doc}/{folder_name}'
        target_folder = conn.web.get_folder_by_server_relative_path(target_folder_url)
        response = target_folder.files.create_upload_session(
            source_path=file_path,
            chunk_size=chunk_size,
            chunk_uploaded=chunk_uploaded,
            **kwargs
        ).execute_query()
        return response

    def get_list(self, sharepoint_site, list_name):
        conn = self._auth(sharepoint_site)
        target_list = conn.web.lists.get_by_title(list_name)
        items = target_list.items.get().execute_query()
        return items

    def get_file_properties_from_folder(self, sharepoint_site, sharepoint_doc, folder_name):
        files_list = self._get_files_list(sharepoint_site, sharepoint_doc, folder_name)
        properties_list = []
        for file in files_list:
            file_dict = {
                'file_id': file.unique_id,
                'file_name': file.name,
                'major_version': file.major_version,
                'minor_version': file.minor_version,
                'file_size': file.length,
                'time_created': file.time_created,
                'time_last_modified': file.time_last_modified
            }
            properties_list.append(file_dict)
        return properties_list

# Testando a listagem de arquivos na biblioteca de documentos 'General'
if __name__ == '__main__':
    sharepoint = SharePoint()
    # files = sharepoint.get_file_properties_from_folder('DWPII')
    # for file in files:
    #     print(file)
