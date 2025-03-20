import os
from dotenv import load_dotenv
from pathlib import Path

# Carregar variáveis de ambiente
load_dotenv()

# Diretórios base
ROOT = os.getenv("ROOT")
BASE_DIR = Path(ROOT)

# Configurações do SharePoint
SHAREPOINT_CONFIG = {
    "url_site": os.getenv("sharepoint_url_site"),
    "site_name": os.getenv("sharepoint_site_name"),
    "doc_library": os.getenv("sharepoint_doc_library"),
    "email": os.getenv("sharepoint_email"),
    "password": os.getenv("sharepoint_password"),
}

# Configurações do SRInfo
SRINFO_CONFIG = {
    "username": os.getenv("USERNAME"),
    "password": os.getenv("PASSWORD"),
    "base_url": "https://srinfo.embrapii.org.br",
}

# Configurações de diretórios
DIRECTORIES = {
    "download": os.getenv("PASTA_DOWNLOAD"),
    "dwpii_copy": BASE_DIR / "DWPII_copy",
    "dwpii_up": BASE_DIR / "DWPII_up",
    "dwpii_backup": BASE_DIR / "DWPII_backup",
}

# Configurações de notificação
NOTIFICATION_CONFIG = {
    "whatsapp_group": "GPE Embrapii",
    "links": {
        "classificacao": "https://embrapii.sharepoint.com/:x:/r/sites/GEPES/Documentos%20Compartilhados/DWPII/srinfo/classificacao_projeto.xlsx?d=wb7a7a439310f4d52a37728b9f1833961&csf=1&web=1&e=qXpfgA",
        "snapshot": "https://embrapii.sharepoint.com/:f:/r/sites/GEPES/Documentos%20Compartilhados/Reports?csf=1&web=1&e=aVdkyL",
    },
}
