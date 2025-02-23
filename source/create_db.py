import sqlite3
import csv

config_filename = 'config.txt'
db_filename = 'schedule.db'

# Function to create tables in the database
def create_tables(db_filename):
    # Connect to the SQLite database (or create it if it doesn't exist)
    conn = sqlite3.connect(db_filename) 
    c = conn.cursor()

    # Create the courses table
    c.execute('''
        CREATE TABLE IF NOT EXISTS courses (
            id INTEGER PRIMARY KEY,
            course_name TEXT NOT NULL,
            student TEXT NOT NULL,
            number_of_students INTEGER NOT NULL,
            class_id INTEGER REFERENCES classrooms(id),
            course_length INTEGER NOT NULL
        );
    ''')

    # Create the students table
    c.execute('''
        CREATE TABLE IF NOT EXISTS students (
            grade TEXT PRIMARY KEY,
            count INTEGER NOT NULL
        );
    ''')

    # Create the classrooms table
    c.execute('''
        CREATE TABLE IF NOT EXISTS classrooms (
            id INTEGER PRIMARY KEY,
            location TEXT NOT NULL,
            current_course_id INTEGER NOT NULL,
            current_course_time_left INTEGER NOT NULL
        );
    ''')

    # Commit changes and close the connection
    conn.commit()
    conn.close()

    print(f"Tables created in the database '{db_filename}'.")

# Call the function to create tables
create_tables(db_filename)

# Function to insert data from config_filename into the database
#def insert_data(db_filename, config_filename):