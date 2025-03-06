from create_db import (create_tables, get_config_file_path, insert_data_from_config, 
                      print_database_content, database_exists, delete_database)
from schedule import run_schedule_loop

def main():
    #if you want to delete the database file, uncomment the next line
    #delete_database('schedule.db')
    db_filename = 'schedule.db'
    
    # Create database if it doesn't exist
    if not database_exists(db_filename):
        print("First time setup - creating new database...")
        config_path = get_config_file_path()
        create_tables(db_filename)
        insert_data_from_config(db_filename, config_path)
        print("\nDatabase created successfully!")
        print_database_content(db_filename)
    else:
        print("Using existing database.")
    
    # Run schedule loop
    print("\nStarting schedule loop...")
    run_schedule_loop()
    print("Schedule loop ended.")

if __name__ == "__main__":
    main()