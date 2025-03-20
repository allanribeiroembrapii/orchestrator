import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


class Config:
    SHAREPOINT_EMAIL = os.getenv("SHAREPOINT_EMAIL")
    SHAREPOINT_PASSWORD = os.getenv("SHAREPOINT_PASSWORD")
    SHAREPOINT_URL_SITE = os.getenv("SHAREPOINT_URL_SITE")
    SHAREPOINT_SITE_NAME = os.getenv("SHAREPOINT_SITE_NAME")
    SHAREPOINT_DOC_LIBRARY = os.getenv("SHAREPOINT_DOC")
    SHAREPOINT_OUTPUT_FOLDER = os.getenv("SHAREPOINT_OUTPUT_FOLDER")
    SHAREPOINT_OUTPUT_FILENAME = os.getenv("SHAREPOINT_OUTPUT_FILENAME")

    # Use absolute path from the project root
    BASE_DIR = Path(__file__).parent
    OUTPUT_DIR = BASE_DIR / "output" / "step_2_data_raw"
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def get_file_path(folder_name, file_name):
        return f"{Config.SHAREPOINT_DOC_LIBRARY}/{folder_name}/{file_name}"
