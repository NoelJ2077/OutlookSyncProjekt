# run.py: Starting point
from app import create_app

# create Flask app
app = create_app()

if __name__ == '__main__':

    # run on all local network interfaces
    app.run(host='0.0.0.0', port=5000, debug=True)
