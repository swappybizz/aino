import bcrypt
def hash_password(password, SECRET_PHR):
    SECRET_PHRASE = SECRET_PHR
    salted_password = (password + SECRET_PHRASE).encode()
    return bcrypt.hashpw(salted_password, bcrypt.gensalt())

# Function to verify passwords
def verify_password(stored_password, provided_password, SECRET_PHR):
    SECRET_PHRASE = SECRET_PHR
    salted_password = (provided_password + SECRET_PHRASE).encode()
    return bcrypt.checkpw(salted_password, stored_password)

# Function to authenticate user
def authenticate(username, password, users_collection, SECRET_PHRASE):
    user = users_collection.find_one({"username": username})
    if user and verify_password(user["password"], password, SECRET_PHRASE):
        return True
    return False

# Function to create a new user
def create_user(username, password, users_collection, SECRET_PHRASE):
    hashed_password = hash_password(password, SECRET_PHRASE)
    users_collection.insert_one({"username": username, "password": hashed_password})
