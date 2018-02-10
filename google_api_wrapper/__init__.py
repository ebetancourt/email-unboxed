import flask
import requests

import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery

class GoogleApiWrapper(object):

    def __init__(self, config):
        self.config = config
        self.current_credentials = None

    def authorize(self):
        # Create flow instance to manage the OAuth 2.0 Authorization Grant Flow steps.
        flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
            self.config.get('CLIENT_SECRETS_FILE'),
            scopes=self.config.get('SCOPES'))

        flow.redirect_uri = flask.url_for(self.config.get('AUTHORIZATION_CALLBACK_ROUTE'), _external=True)

        authorization_url, state = flow.authorization_url(
            # Enable offline access so that you can refresh an access token without
            # re-prompting the user for permission. Recommended for web server apps.
            access_type='offline',
            # Enable incremental authorization. Recommended as a best practice.
            include_granted_scopes='true')

        # Store the state so the callback can verify the auth server response.
        self._save_state(state)
        return flask.redirect(authorization_url)

    def store_authorization(self, request_uri):
        state = self._get_state()

        flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
            self.config.get('CLIENT_SECRETS_FILE'),
            scopes=self.config.get('SCOPES'),
            state=state)
        flow.redirect_uri = flask.url_for(self.config.get('AUTHORIZATION_CALLBACK_ROUTE'), _external=True)

        # Use the authorization server's response to fetch the OAuth 2.0 tokens.
        authorization_response = request_uri
        flow.fetch_token(authorization_response=authorization_response)

        self._save_credentials(flow.credentials)

    def get_service(self, api_service_name=None, api_version=None):
        if api_service_name is None:
            api_service_name = self.config.get('API_SERVICE_NAME')
        if api_version is None:
            api_version = self.config.get('API_VERSION')

        credentials = self.get_saved_credentials()
        service = googleapiclient.discovery.build(api_service_name, api_version, credentials=credentials)
        self.current_credentials = credentials
        return service

    def save_service_credentials(self):
        if self.current_credentials is not None:
            self._save_credentials(self.current_credentials)

    def revoke(self):
        credentials = self.get_saved_credentials()
        revoke_call = requests.post('https://accounts.google.com/o/oauth2/revoke',
                                    params={'token': credentials.token},
                                    headers={'content-type': 'application/x-www-form-urlencoded'})

        status_code = getattr(revoke_call, 'status_code')
        return status_code == 200

    def clear(self):
        if 'credentials' in flask.session:
            del flask.session['credentials']
        return True

    def get_saved_credentials(self):
        return google.oauth2.credentials.Credentials(**flask.session['credentials'])

    def credentials_available(self):
        return 'credentials' in flask.session

    def _credentials_to_dict(self, credentials):
        return {'token': credentials.token,
                'refresh_token': credentials.refresh_token,
                'token_uri': credentials.token_uri,
                'client_id': credentials.client_id,
                'client_secret': credentials.client_secret,
                'scopes': credentials.scopes}

    def _save_credentials(self, credentials):
        # Store credentials in the session.
        # ACTION ITEM: In a production app, you likely want to save these
        #              credentials in a persistent database instead.
        flask.session['credentials'] = self._credentials_to_dict(credentials)

    def _save_state(self, state):
        flask.session['state'] = state

    def _get_state(self):
        return flask.session['state']
