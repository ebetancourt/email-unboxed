GMAIL_API = {
    'CLIENT_SECRETS_FILE': "client_secret.json",
    'SCOPES': ['https://www.googleapis.com/auth/gmail.modify'],
    'API_SERVICE_NAME': 'gmail',
    'API_VERSION': 'v1',
    'AUTHORIZATION_CALLBACK_ROUTE': 'google_auth_blueprint.oauth2callback'
}
# This OAuth 2.0 access scope allows for full read/write access to the
# authenticated user's account and requires requests to use an SSL connection.
