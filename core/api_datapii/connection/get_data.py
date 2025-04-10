from .sharepoint import sharepoint_get
from .api_query import api_ibge


def get_data():
    sharepoint_get()
    api_ibge()