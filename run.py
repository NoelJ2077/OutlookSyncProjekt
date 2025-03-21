# run.py: Starting point
from app import create_app
# testing 
from app.ignore.hashing import hash_password
from app.config import Tests
import requests

# create Flask app
app = create_app()

if __name__ == '__main__':

    # create a default admin user
    hashed_pw = hash_password(Tests.password)
    Tests.create_user(hashed_pw)

    # run on all local network interfaces
    app.run(host='0.0.0.0', port=5000, debug=True)
