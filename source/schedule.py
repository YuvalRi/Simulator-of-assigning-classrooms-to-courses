import sqlite3
import time
from create_db import database_exists

def is_courses_table_empty(cursor):
    """Check if the courses table is empty"""
    cursor.execute("SELECT COUNT(*) FROM courses")
    count = cursor.fetchone()[0]
    return count == 0

def get_available_classrooms(cursor):
    """Get classrooms with no current course (time_left = 0)"""
    cursor.execute("SELECT id FROM classrooms WHERE current_course_time_left = 0")
    return [row[0] for row in cursor.fetchall()]

def get_unassigned_courses(cursor):
    """Get courses ordered by input order (id)"""
    cursor.execute("SELECT id, class_id, course_length FROM courses ORDER BY id")
    return cursor.fetchall()

def update_student_count(cursor, student_type, num_students):
    """Update the count of available students when a course is assigned"""
    cursor.execute("""
        UPDATE students 
        SET count = count - ? 
        WHERE grade = ? AND count >= ?
    """, (num_students, student_type, num_students))
    return cursor.rowcount > 0

def get_course_details(cursor, course_id):
    """Get course details including student type and number of students"""
    cursor.execute("""
        SELECT course_name, student, number_of_students 
        FROM courses 
        WHERE id = ?
    """, (course_id,))
    return cursor.fetchone()

def assign_course_to_classroom(cursor, course_id, classroom_id, course_length):
    """Assign a course to an available classroom if enough students are available"""
    # Get course details
    course_details = get_course_details(cursor, course_id)
    if not course_details:
        return False
    
    _, student_type, num_students = course_details
    
    # Check if enough students are available
    if update_student_count(cursor, student_type, num_students):
        # If successful, update classroom
        cursor.execute("""
            UPDATE classrooms 
            SET current_course_id = ?, current_course_time_left = ? 
            WHERE id = ?
        """, (course_id, course_length, classroom_id))
        return True
    return False

def get_course_name(cursor, course_id):
    """Get course name by id"""
    cursor.execute("SELECT course_name FROM courses WHERE id = ?", (course_id,))
    result = cursor.fetchone()
    return result[0] if result else None

def get_classroom_location(cursor, classroom_id):
    """Get classroom location by id"""
    cursor.execute("SELECT location FROM classrooms WHERE id = ?", (classroom_id,))
    result = cursor.fetchone()
    return result[0] if result else None

def get_occupied_classrooms(cursor):
    """Get classrooms that are currently occupied"""
    cursor.execute("""
        SELECT id, current_course_id, location 
        FROM classrooms 
        WHERE current_course_time_left > 0
    """)
    return cursor.fetchall()

def get_completed_courses(cursor):
    """Get courses that just finished"""
    cursor.execute("""
        SELECT c.id, c.course_name, cl.id, cl.location
        FROM classrooms cl
        JOIN courses c ON c.id = cl.current_course_id
        WHERE cl.current_course_time_left = 0 AND cl.current_course_id != 0
    """)
    return cursor.fetchall()

def print_current_state(cursor):
    """Print current state of all tables after each iteration"""
    print("\n=== Current Database State ===")
    
    # Print courses table
    print("\ncourses")
    cursor.execute("SELECT * FROM courses ORDER BY id")
    courses = cursor.fetchall()
    for course in courses:
        print(course)
    
    # Print students table
    print("\nstudents")
    cursor.execute("SELECT * FROM students ORDER BY grade")
    students = cursor.fetchall()
    for student in students:
        print(student)
    
    # Print classrooms table
    print("\nclassrooms")
    cursor.execute("SELECT * FROM classrooms ORDER BY id")
    classrooms = cursor.fetchall()
    for classroom in classrooms:
        print(classroom)
    print("\n")

def run_schedule_loop():
    db_filename = 'schedule.db'
    iteration = 1
    
    while True:
        if not database_exists(db_filename):
            print("Database does not exist. Exiting schedule loop.")
            break
            
        try:
            conn = sqlite3.connect(db_filename)
            cursor = conn.cursor()
            
            if is_courses_table_empty(cursor):
                print("All courses are completed. Exiting schedule loop.")
                break

            # First handle occupied classrooms
            occupied_rooms = get_occupied_classrooms(cursor)
            for room_id, course_id, location in occupied_rooms:
                course_name = get_course_name(cursor, course_id)
                print(f"({iteration}) {location}: occupied by {course_name}")

            # Update time left for occupied rooms
            cursor.execute("""
                UPDATE classrooms 
                SET current_course_time_left = current_course_time_left - 1 
                WHERE current_course_time_left > 0
            """)

            # Handle completed courses and immediate reassignment
            completed_courses = get_completed_courses(cursor)
            for course_id, course_name, room_id, location in completed_courses:
                # Print completion message
                print(f"({iteration}) {location}: {course_name} is done")
                
                # Remove completed course
                cursor.execute("DELETE FROM courses WHERE id = ?", (course_id,))
                
                # Reset classroom course_id
                cursor.execute("""
                    UPDATE classrooms 
                    SET current_course_id = 0, current_course_time_left = 0 
                    WHERE id = ?
                """, (room_id,))
                
                # Try to assign new course immediately
                available_courses = get_unassigned_courses(cursor)
                for new_course_id, preferred_room, course_length in available_courses:
                    if preferred_room == room_id:
                        if assign_course_to_classroom(cursor, new_course_id, room_id, course_length):
                            new_course_name = get_course_name(cursor, new_course_id)
                            print(f"({iteration}) {location}: {new_course_name} is scheduled to start")
                            break

            # Handle remaining available classrooms
            available_classrooms = get_available_classrooms(cursor)
            if available_classrooms:
                courses = get_unassigned_courses(cursor)
                for course_id, preferred_room, course_length in courses:
                    if preferred_room in available_classrooms:
                        if assign_course_to_classroom(cursor, course_id, preferred_room, course_length):
                            course_name = get_course_name(cursor, course_id)
                            classroom_location = get_classroom_location(cursor, preferred_room)
                            available_classrooms.remove(preferred_room)
                            print(f"({iteration}) {classroom_location}: {course_name} is scheduled to start")
            
            # Print current state after all operations
            print(f"\n--- After Iteration {iteration} ---")
            print_current_state(cursor)
            
            conn.commit()
            iteration += 1
            
        except Exception as e:
            print(f"Error in schedule loop: {e}")
            break
        finally:
            if 'conn' in locals():
                conn.close()
