# run.py: Starting point
from app import create_app
# testing 
from app.ignore.hashing import hash_password
from app.config import Tests

import requests, socket, logging

# create Flask app
app = create_app()
logger = logging.getLogger(__name__)

if __name__ == '__main__':
    # create a default admin user
    hashed_pw = hash_password(Tests.password)
    Tests.create_user(hashed_pw)

    # get local host IPv4 address
    host_ipv4 = socket.gethostbyname(socket.gethostname())
    logger.info(f"Local host IPv4 address: {host_ipv4}")

    # run on all local network interfaces
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=True)
    