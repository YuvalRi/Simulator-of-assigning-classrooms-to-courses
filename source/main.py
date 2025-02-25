from create_db import (create_tables, get_config_file_path, insert_data_from_config, 
                      print_database_content, database_exists, delete_database)

def main():
    #if you want to delete the database file, uncomment the next line
    #delete_database('schedule.db')
    db_filename = 'schedule.db'
    
    # Exit if database already exists
    if database_exists(db_filename):
        print("Database already exists.")
        return
        
    # First time setup
    print("First time setup - creating new database...")
    config_path = get_config_file_path()
    
    # Create and populate database
    create_tables(db_filename)
    insert_data_from_config(db_filename, config_path)
    print("\nDatabase created successfully!")
    
    # Print initial database content
    print_database_content(db_filename)

if __name__ == "__main__":
    main()