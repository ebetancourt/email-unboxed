import os
import flask

from api import api
from google_auth_blueprint import google_auth_blueprint

app = flask.Flask(__name__)

app.config.from_object('config.config')
app.config.from_object('config.gmail_api')

app.secret_key = app.config.get('SECRET_KEY')
app.register_blueprint(api, url_prefix='/api/v1')
app.register_blueprint(google_auth_blueprint, url_prefix='/auth')


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def index(path):
    return flask.render_template('index.html', path=path)


if __name__ == '__main__':
    # When running locally, disable OAuthlib's HTTPs verification.
    # ACTION ITEM for developers:
    #     When running in production *do not* leave this option enabled.
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

    # Specify a hostname and port that are set as a valid redirect URI
    # for your API project in the Google API Console.
    app.run('localhost', 8080, debug=True)
