#!/usr/bin/env python
import os
import json
import logging

import requests
import msal
from dotenv import load_dotenv
load_dotenv()

# Optional logging
# logging.basicConfig(level=logging.DEBUG)

app_authority = os.getenv('AAD_AUTHORITY')
client_id = os.getenv('PY_CLIENT_ID')
app_secret = os.getenv('PY_APP_SECRET')

attrs = "givenname,sn,mail,officelocation,streetaddress,city,state,\
         postalcode,country"
app_scopes = ["https://graph.microsoft.com/.default"]
app_endpoint = f'https://graph.microsoft.com/beta/users?select={attrs}'


# Create a preferably long-lived app instance which maintains a token cache.
app = msal.ConfidentialClientApplication(
    client_id, authority=app_authority,
    client_credential=app_secret,
    )

# The pattern to acquire a token looks like this.
result = None

# Firstly, looks up a token from cache
# Since we are looking for token for the current app, NOT for an end user,
# notice we give account parameter as None.
result = app.acquire_token_silent(app_scopes, account=None)

if not result:
    logging.info("No suitable token exists in cache. Let's get a new one.")
    result = app.acquire_token_for_client(scopes=app_scopes)

if "access_token" in result:
    # Calling graph using the access token
    graph_data = requests.get(  # Use token to call downstream service
        app_endpoint,
        headers={'Authorization': 'Bearer ' + result['access_token']}, ).json()
    print("Graph API call result: ")
    print(json.dumps(graph_data, indent=2))
else:
    print(result.get("error"))
    print(result.get("error_description"))
    print(result.get("correlation_id"))
