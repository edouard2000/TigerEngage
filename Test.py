import db_operations

def setup_initial_data():
    # Create professor
    professor_netid = "ek4149"
    if db_operations.create_user(professor_netid, 'professor'):
        print(f"Professor {professor_netid} created successfully.")

        # Create class
        class_title = "Advanced Computational Methods"
        class_created, class_id = db_operations.create_class_for_professor(professor_netid, class_title)
        if class_created:
            print(f"Class '{class_title}' created. Class ID: {class_id}")

            # Create question
            question_text = "What is the derivative of x^2?"
            correct_answer = "2x"
            question_id = db_operations.add_question_to_class(class_id, question_text, correct_answer)
            if question_id:
                print(f"Question '{question_text}' added to class {class_id} with ID {question_id}")
                
                # Simulate multiple student answers
                students = ["student001", "student002", "student003"]
                answers = ["I am not sure what is the right answer", "may be it is: 2", "it is exactly: x^2"]
                for student_netid, answer in zip(students, answers):
                    if not db_operations.user_exists(student_netid):
                        db_operations.create_user(student_netid, 'student')
                    db_operations.submit_answer_for_question(question_id, student_netid, answer)
                    print(f"Answer '{answer}' submitted by {student_netid} for question {question_id}")

            else:
                print("Failed to add question.")
        else:
            print(f"Failed to create class '{class_title}' for Professor {professor_netid}.")
    else:
        print(f"Failed to create professor {professor_netid}.")

if __name__ == '__main__':
    setup_initial_data()
