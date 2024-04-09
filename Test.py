import db_operations

def setup_initial_data():
    # Create professor
    professor_netid = "ek4149"
    if db_operations.create_user(professor_netid, 'professor'):
        print(f"Professor {professor_netid} created successfully.")
        # Create class
        class_title = "COS333"
        class_created, class_id = db_operations.create_class_for_professor(professor_netid, class_title)
        if class_created:
            print(f"Class '{class_title}' created for Professor {professor_netid}. Class ID: {class_id}")
            # Start a session
            session_started, session_id = db_operations.start_new_session(class_id)
            if session_started:
                print("Session started successfully for class", class_title)
                # Create student and enroll in class
                student_netid = "student01"
                if db_operations.create_user(student_netid, 'student'):
                    print(f"Student {student_netid} created successfully.")
                    # Enroll student in class
                    if db_operations.enroll_student(student_netid, class_id):
                        print(f"Student {student_netid} enrolled in class '{class_title}' successfully.")
                        # Record attendance and update score
                        attendance_recorded, message = db_operations.record_attendance_and_update(student_netid, class_id, session_id)
                        if attendance_recorded:
                            print(message)
                        else:
                            print("Failed to record attendance:", message)
                    else:
                        print(f"Failed to enroll student {student_netid} in class '{class_title}'.")
                else:
                    print(f"Failed to create student {student_netid}.")
            else:
                print("Failed to start session for class", class_title)
        else:
            print(f"Failed to create class '{class_title}' for Professor {professor_netid}.")
    else:
        print(f"Failed to create professor {professor_netid}.")

if __name__ == '__main__':
    setup_initial_data()
