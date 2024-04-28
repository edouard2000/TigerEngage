from db_operations import create_user, create_class_for_professor, start_new_session

# Define user information
netid = "jdoe2024"  # Dummy NetID
role = "professor"  # Role can be 'student' or 'professor'

# Create user
user_creation_success = create_user(netid, role)
print(f"User creation successful: {user_creation_success}")

if user_creation_success and role == "professor":
    # Define class information if the user is a professor
    class_title = "Introduction to Computer Science"

    # Create a class for the professor
    class_creation_success, class_id = create_class_for_professor(netid, class_title)
    print(f"Class creation successful: {class_creation_success}, Class ID: {class_id}")

    if class_creation_success:
        # Start a new session for the created class
        session_start_success, session_id = start_new_session(class_id)
        print(f"Session start successful: {session_start_success}, Session ID: {session_id}")
else:
    print("User must be a professor to create a class.")
