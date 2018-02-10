import flask
import requests
import json

import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery

from google_api_wrapper import GoogleApiWrapper

google_auth_blueprint = flask.Blueprint('google_auth_blueprint', __name__)

# This variable specifies the name of a file that contains the OAuth 2.0
# information for this application, including its client_id and client_secret.


@google_auth_blueprint.route('/')
@google_auth_blueprint.route('/test')
def test_api_request():
    google_wrapper = get_api_wrapper()
    if not google_wrapper.credentials_available():
        return flask.redirect(flask.url_for('google_auth_blueprint.authorize'))

    service = google_wrapper.get_service()
    results = service.users().labels().list(userId='me').execute()
    labels = results.get('labels', [])

    # Save credentials back to session in case access token was refreshed.
    google_wrapper.save_service_credentials()

    return json.dumps(labels)


@google_auth_blueprint.route('/authorize')
def authorize():
    gWrapper = get_api_wrapper()
    return gWrapper.authorize()


@google_auth_blueprint.route('/oauth2callback')
def oauth2callback():
    google_wrapper = get_api_wrapper()
    google_wrapper.store_authorization(flask.request.url)
    return flask.redirect(flask.url_for('google_auth_blueprint.test_api_request'))


@google_auth_blueprint.route('/revoke')
def revoke():
    google_wrapper = get_api_wrapper()
    success = google_wrapper.revoke()

    if success:
        return 'Credentials successfully revoked.' + print_index_table()
    else:
        return 'An error occurred.' + print_index_table()


@google_auth_blueprint.route('/clear')
def clear_credentials():
    google_wrapper = get_api_wrapper()
    google_wrapper.clear()
    return ('Credentials have been cleared.<br><br>' +
            print_index_table())


def print_index_table():
    return ('<table>' +
            '<tr><td><a href="' + flask.url_for('google_auth_blueprint.test_api_request') +
            '">Test an API request</a></td>' +
            '<td>Submit an API request and see a formatted JSON response. ' +
            '    Go through the authorization flow if there are no stored ' +
            '    credentials for the user.</td></tr>' +
            '<tr><td><a href="' + flask.url_for('google_auth_blueprint.authorize') +
            '">Test the auth flow directly</a></td>' +
            '<td>Go directly to the authorization flow. If there are stored ' +
            '    credentials, you still might not be prompted to reauthorize ' +
            '    the application.</td></tr>' +
            '<tr><td><a href="' + flask.url_for('google_auth_blueprint.revoke') +
            '">Revoke current credentials</a></td>' +
            '<td>Revoke the access token associated with the current user ' +
            '    session. After revoking credentials, if you go to the test ' +
            '    page, you should see an <code>invalid_grant</code> error.' +
            '</td></tr>' +
            '<tr><td><a href="' + flask.url_for('google_auth_blueprint.clear_credentials') +
            '">Clear Flask session credentials</a></td>' +
            '<td>Clear the access token currently stored in the user session. ' +
            '    After clearing the token, if you <a href="/test">test the ' +
            '    API request</a> again, you should go back to the auth flow.' +
            '</td></tr></table>')

def get_api_wrapper():
    app = flask.current_app
    return GoogleApiWrapper(app.config.get('GMAIL_API'))
