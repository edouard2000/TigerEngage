import db_operations

def create_dummy_data():
    professor_netid = "prof_dummy"
    class_title = "Dummy Class for Testing"
    if db_operations.create_user(professor_netid, 'professor'):
        print(f"Professor {professor_netid} created successfully.")
        class_created, class_id = db_operations.create_class_for_professor(professor_netid, class_title)
        if class_created:
            print(f"Class '{class_title}' created for Professor {professor_netid}. Class ID: {class_id}")
            if start_class_session(class_id):
                print(f"Active session for class '{class_id}' started.")
        else:
            print(f"Failed to create class '{class_title}' for Professor {professor_netid}.")
    else:
        print(f"Failed to create professor {professor_netid}.")

def start_class_session(class_id):
    session = db_operations.start_new_session(class_id)
    if session:
        print(f"Session {session.session_id} for class {class_id} started at {session.start_time}")
        return True
    else:
        print(f"Failed to start session for class {class_id}.")
        return False

if __name__ == '__main__':
    create_dummy_data()
