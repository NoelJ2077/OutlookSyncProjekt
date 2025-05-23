# More Soon!

# Description
- School project :D
- Web app that retrieves all contacts of a specific user within a tenant.
- **Create**, **edit**, **delete**, and **update** contacts via the web interface and sync the changes with your Microsoft Outlook Exchange account!

# Requirements
- Flask==3.1.0
- python-dotenv==1.0.1
- python_bcrypt==0.3.2
- Requests==2.32.3
  
# .gitignore
- You will need to implement your own password-saving method and configure the .env variables.
- Client_ID=client_id_string
- Client_Secret=client_secret_key_string
- Tenant_ID=tenant_string
- SECRET_KEY=secret_key_string_for_flask
- REDIRECT_URI=http://localhost:5000/callback # 5000 -> Flask default port

# Project structure from root /folder:
requirements.txt
run.py
app/
    __init.py__
    client_actions.py
    client.py
    config.py
    helpermethods.py
    routes.py
    ignore/
        app.log
        contacts.db
        .env
        hashing.py
    static/
        dashboard.css
        # standard Flask files.
    templates/
        index.html
        # All html pages
