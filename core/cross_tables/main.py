from connection.get_sharepoint import get_files_from_sharepoint
from start_clean import start_clean


def cross_tables():

    #Start clean
    start_clean()

    #Get files
    get_files_from_sharepoint()

      

if __name__ == "__main__":
    cross_tables()
