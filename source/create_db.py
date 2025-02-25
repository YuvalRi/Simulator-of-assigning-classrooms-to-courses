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

# Connect to the SQLite database
conn = sqlite3.connect(db_filename) 
c = conn.cursor()

def insert_data_from_config(connection):
    file_path = 'config.txt'
    cursor = connection.cursor()
    
    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()

            if line:
                parts = [part.strip() for part in line.split(',')]
                first_letter = parts[0].upper()
                
                if first_letter == 'C':
                    if len(parts) >= 7:
                        cursor.execute('''INSERT INTO courses 
                            (id, course_name, student, number_of_students, class_id, course_length) 
                            VALUES (?, ?, ?, ?, ?, ?)''',
                            (parts[1], parts[2], parts[3], parts[4], parts[5], parts[6]))
                
                elif first_letter == 'S':
                    if len(parts) >= 3:
                        cursor.execute('INSERT INTO students (grade, count) VALUES (?, ?)',
                            (parts[1], parts[2]))
                
                elif first_letter == 'R':
                    if len(parts) >= 3:
                        cursor.execute('''INSERT INTO classrooms 
                            (id, location, current_course_id, current_course_time_left) 
                            VALUES (?, ?, 0, 0)''',
                            (parts[1], parts[2]))
                            
    connection.commit()
    print("Data inserted into the database.")

# Call the function to insert data from the configuration file
insert_data_from_config(conn)
