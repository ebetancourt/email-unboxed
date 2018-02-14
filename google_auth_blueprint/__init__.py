import flask
import json

from google_api_wrapper import GoogleApiWrapper

google_auth_blueprint = flask.Blueprint('google_auth_blueprint', __name__)


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
    google_wrapper = get_api_wrapper()
    return google_wrapper.authorize()


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
    return 'Credentials have been cleared.<br><br>' + print_index_table()


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


@google_auth_blueprint.route('/emails')
def pull_label_emails():
    google_wrapper = get_api_wrapper()
    if not google_wrapper.credentials_available():
        return flask.redirect(flask.url_for('google_auth_blueprint.authorize'))

    service = google_wrapper.get_service()
    messages = ListMessagesWithLabels(service, 'me', ['Label_49'])
    google_wrapper.save_service_credentials()
    user_profile = service.users().getProfile(userId='me').execute()
    user_email = user_profile['emailAddress']

    message_list = []
    for message in messages:
        subject = next(iter([x for x in message['payload']['headers'] if x['name'] ==
                        'Subject']))
        message_list.append({
            "subject": subject['value'],
            "link" :
            'https://mail.google.com/mail/u/{}/#inbox/{}'.format(user_email, message['id']),
            "snippet":message['snippet']
        })

    return json.dumps(message_list)

def ListMessagesWithLabels(service, user_id, label_ids=[]):
    """List all Messages of the user's mailbox with label_ids applied.

    Args:
    service: Authorized Gmail API service instance.
    user_id: User's email address. The special value "me"
    can be used to indicate the authenticated user.
    label_ids: Only return Messages with these labelIds applied.

    Returns:
    List of Messages that have all required Labels applied. Note that the
    returned list contains Message IDs, you must use get with the
    appropriate id to get the details of a Message.
    """
    response = service.users().messages().list(userId=user_id,
                             q='after:1518472800 before:1518559200',
                                           labelIds=label_ids).execute()
    messages = []
    if 'messages' in response:
        messages.extend(response['messages'])

    while 'nextPageToken' in response:
        page_token = response['nextPageToken']
        response = service.users().messages().list(userId=user_id,
                                                 labelIds=label_ids,
                             q='after:1518472800 before:1518559200',
                                                 pageToken=page_token).execute()
        messages.extend(response['messages'])

    full_messages = []
    for email in messages:
        full_messages.append(service.users().messages().get(userId=user_id, id=email['id'],
                                             format='full').execute())

    return full_messages
