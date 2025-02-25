import sqlite3
import os

def delete_database(db_filename):
    """Delete the database file if it exists"""
    try:
        if os.path.exists(db_filename):
            os.remove(db_filename)
            print(f"Database {db_filename} deleted successfully")
    except Exception as e:
        print(f"Error deleting database: {e}")

def database_exists(db_filename):
    """Check if database file exists"""
    return os.path.exists(db_filename)

# Create a new SQLite database with the given filename
# Create tables for courses, students, and classrooms
def create_tables(db_filename):
    conn = sqlite3.connect(db_filename)
    cursor = conn.cursor()

    try:
        cursor.execute("""CREATE TABLE IF NOT EXISTS courses (
                        id INTEGER PRIMARY KEY,
                        course_name TEXT NOT NULL,
                        student TEXT NOT NULL,
                        number_of_students INTEGER NOT NULL,
                        class_id INTEGER REFERENCES classrooms(id),
                        course_length INTEGER NOT NULL)""")
                        
        cursor.execute("""CREATE TABLE IF NOT EXISTS students (
                        grade TEXT PRIMARY KEY, 
                        count INTEGER NOT NULL)""")
                        
        cursor.execute("""CREATE TABLE IF NOT EXISTS classrooms (
                        id INTEGER PRIMARY KEY, 
                        location TEXT NOT NULL, 
                        current_course_id INTEGER NOT NULL, 
                        current_course_time_left INTEGER NOT NULL)""")
                        
        conn.commit()
        print("Tables created successfully")
    except Exception as e:
        print(f"Error creating tables: {e}")
    finally:
        conn.close()

def get_config_file_path():
    while True:
        file_path = input("Enter config file path: ").strip().strip('"\'')
        if file_path:
            return file_path
        print("Path cannot be empty. Please try again.")

def reset_tables(db_filename):
    """Clear all data from tables in the database so new data can be inserted.
    Otherwise, many warnings will be raised when trying to insert data that already exists."""
    conn = sqlite3.connect(db_filename)
    cursor = conn.cursor()
    
    try:
        cursor.execute("DELETE FROM courses")
        cursor.execute("DELETE FROM students")
        cursor.execute("DELETE FROM classrooms")
        conn.commit()
        print("Tables reset successfully")
    except Exception as e:
        print(f"Error resetting tables: {e}")
    finally:
        conn.close()

def insert_data_from_config(db_filename, config_path):
    conn = sqlite3.connect(db_filename)
    cursor = conn.cursor()
    
    try:
        with open(config_path, 'r') as file:
            for line_number, line in enumerate(file, 1):
                line = line.strip()
                if not line:
                    continue
                
                parts = [p.strip() for p in line.split(',')]
                first_letter = parts[0].upper()
                
                if first_letter == 'C' and len(parts) >= 7:
                    cursor.execute("INSERT INTO courses VALUES (?, ?, ?, ?, ?, ?)", 
                                 (parts[1], parts[2], parts[3], parts[4], parts[5], parts[6]))
                elif first_letter == 'S' and len(parts) >= 3:
                    cursor.execute("INSERT INTO students VALUES (?, ?)", 
                                 (parts[1], parts[2]))
                elif first_letter == 'R' and len(parts) >= 3:
                    cursor.execute("INSERT INTO classrooms VALUES (?, ?, 0, 0)", 
                                 (parts[1], parts[2]))
                    
        conn.commit()
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
    finally:
        conn.close()

def print_database_content(db_filename):
    """Print the content of all tables in the database"""
    conn = sqlite3.connect(db_filename)
    cursor = conn.cursor()
    
    try:
        print("\n=== Database Content ===")
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        # Print content of each table
        for table in tables:
            table_name = table[0]
            if table_name != 'sqlite_sequence':  # Skip SQLite internal table
                print(f"\n{table_name}")
                cursor.execute(f"SELECT * FROM {table_name}")
                rows = cursor.fetchall()
                for row in rows:
                    print(row)
    except Exception as e:
        print(f"Error printing database content: {e}")
    finally:
        conn.close()