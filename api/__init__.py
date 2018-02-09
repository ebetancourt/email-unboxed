from flask import Blueprint

api = Blueprint('api', __name__)


@api.route('/', defaults={'path': ''})
@api.route('/<path:path>')
def show(path):
    return ' you want pages: /%s' % path
