import db_operations

def setup_initial_data():
    # Create professor
    professor_netid = "prof002"
    if db_operations.create_user(professor_netid, 'professor'):
        print(f"Professor {professor_netid} created successfully.")

        # Create class
        class_title = "COS444"
        class_created, class_id = db_operations.create_class_for_professor(professor_netid, class_title)
        if class_created:
            print(f"Class '{class_title}' created. Class ID: {class_id}")
            
            # Start a session
            session_started, session_id = db_operations.start_new_session(class_id)
            if session_started:
                print(f"Session started for class {class_title}")
                
                # Create questions
                question1_id = db_operations.add_question_to_class(class_id, "What is the capital of France?", "Paris")
                print(f"Question added to class {class_id} with ID {question1_id}")
                
                question2_id = db_operations.add_question_to_class(class_id, "What is the largest ocean on Earth?", "Pacific Ocean")
                print(f"Question added to class {class_id} with ID {question2_id}")
                
                # Activate the first question
                if db_operations.update_question_status(question1_id, class_id, True):
                    print(f"Question {question1_id} activated.")
                else:
                    print(f"Failed to activate question {question1_id}.")
                
                # Create student and enroll in class
                student_netid = "student123"
                if db_operations.create_user(student_netid, 'student'):
                    print(f"Student {student_netid} created successfully.")
                    
                    if db_operations.enroll_student(student_netid, class_id):
                        print(f"Student {student_netid} enrolled in class '{class_title}' successfully.")
                        
                        if db_operations.record_attendance_and_update(student_netid, class_id, session_id):
                            print(f"Attendance recorded for student {student_netid} in class {class_title}.")
                        else:
                            print(f"Failed to record attendance for student {student_netid}.")
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
