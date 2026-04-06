import streamlit as st
from pymongo import MongoClient
from datetime import datetime

# --- MongoDB Connection Setup ---
# Connect to local MongoDB instance
MONGO_URI = "mongodb+srv://tomcr00ze:Shiv@m9211@cluster-aj.oen2mzu.mongodb.net/?appName=Cluster-AJ"
client = MongoClient(MONGO_URI)
db = client['streamlit_todo_app']
users_collection = db['users']
tasks_collection = db['tasks']

# --- Session State Initialization ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'username' not in st.session_state:
    st.session_state['username'] = ''

# --- Helper Functions ---
def create_user(username, password):
    # Note: In a real app, always hash passwords (e.g., using bcrypt). 
    # Stored in plaintext here purely for the simplicity of the demo.
    if users_collection.find_one({"username": username}):
        return False
    users_collection.insert_one({"username": username, "password": password})
    return True

def authenticate_user(username, password):
    user = users_collection.find_one({"username": username, "password": password})
    return user is not None

# --- UI: Authentication ---
if not st.session_state['logged_in']:
    st.title("MongoDB + Streamlit App")
    
    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    
    with tab1:
        st.subheader("Login")
        login_user = st.text_input("Username", key="login_user")
        login_pass = st.text_input("Password", type="password", key="login_pass")
        if st.button("Login"):
            if authenticate_user(login_user, login_pass):
                st.session_state['logged_in'] = True
                st.session_state['username'] = login_user
                st.rerun()
            else:
                st.error("Invalid username or password")

    with tab2:
        st.subheader("Create New Account")
        signup_user = st.text_input("New Username")
        signup_pass = st.text_input("New Password", type="password")
        if st.button("Sign Up"):
            if create_user(signup_user, signup_pass):
                st.success("Account created successfully! Please log in.")
            else:
                st.error("Username already exists.")

# --- UI: Todo Application (Logged In) ---
else:
    st.title(f"Welcome, {st.session_state['username']}!")
    
    if st.button("Logout"):
        st.session_state['logged_in'] = False
        st.session_state['username'] = ''
        st.rerun()

    st.markdown("---")
    st.header("Your Task List")

    # CREATE Task
    with st.form("new_task_form", clear_on_submit=True):
        new_task = st.text_input("Add a new task:")
        submitted = st.form_submit_button("Add Task")
        if submitted and new_task:
            tasks_collection.insert_one({
                "username": st.session_state['username'],
                "task": new_task,
                "status": "pending",
                "created_at": datetime.now()
            })
            st.success("Task added!")

    # READ and Display Tasks
    user_tasks = list(tasks_collection.find({"username": st.session_state['username']}))
    
    if not user_tasks:
        st.info("No tasks yet. Add one above!")
    else:
        for task in user_tasks:
            col1, col2, col3 = st.columns([0.6, 0.2, 0.2])
            
            # Display task with strikethrough if completed
            if task['status'] == "completed":
                col1.write(f"~~{task['task']}~~")
            else:
                col1.write(task['task'])
            
            # UPDATE Task Status
            if task['status'] == "pending":
                if col2.button("Complete", key=f"comp_{task['_id']}"):
                    tasks_collection.update_one(
                        {"_id": task['_id']},
                        {"$set": {"status": "completed"}}
                    )
                    st.rerun()
            
            # DELETE Task
            if col3.button("Delete", key=f"del_{task['_id']}"):
                tasks_collection.delete_one({"_id": task['_id']})
                st.rerun()