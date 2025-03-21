from app.client import GraphClient

def get_export():
    # Export 1 contact to outlook
    export = {
    "displayName": "Peter Meier",
    "emailAddresses": [
        {"name": "Peter Meier", "address": "p.meier@gmx.ch"}
    ],
    "businessPhones": ["+41 79 123 45 67"],
    "companyName": "Meier Elektronik AG",
    "jobTitle": "CEO"
    }

    return export

def test_export():
    client = GraphClient()
    client.get_access_token()

    test_contact = {
        "displayName": "Peter Meier",
        "emailAddresses": [{"name": "Peter Meier", "address": "p.meier@gmx.ch"}],
        "businessPhones": ["+41 79 123 45 67"],
        "companyName": "Meier Elektronik AG",
        "jobTitle": "CEO"
    }

    assert client.export_contact([test_contact]) is True