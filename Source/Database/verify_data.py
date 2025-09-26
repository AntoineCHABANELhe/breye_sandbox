from Source.Database.db_enums import Table
from Source.Database.handle_database import HandleDB

def verify_db():
    """Check if the DB is operational. If not, repair it and returns False"""

    all_tables_exist = True
    
    for tab in Table:
        if not HandleDB().table_exists(tab.value):
            all_tables_exist = False
            break

    # # Retourne True si la base n'a pas eu besoin d'être altérée
    return all_tables_exist

if __name__ == "__main__":
    verify_db()