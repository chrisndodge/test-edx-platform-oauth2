from flask import Flask, render_template, session, request,\
        make_response, redirect, abort, jsonify
from flask_oauthlib.client import OAuth
import jwt


app = Flask(__name__)
app.config.from_object('settings')
app.secret_key = '\xc8K\x80\x00e}R\x92I\x1b\xec\x10"oP\xc5o~~\x83\xb6f\x9e4'
# be sure to set debug so we get stack trace
app.debug = True

DEBUG = True

oauth = OAuth()
open_edx_remote = None
access_token = None


def login():
    print 'here'
    response = open_edx_remote.authorize(
        scope='identity',
        callback='http://localhost:5000/redirect'.format(app.config['BASE_HOSTNAME'])
    )

    return response

def redirect():

    if request.args.get('error') == 'access_denied':
        return "User declined"

    response = open_edx_remote.authorized_response()

    global access_token
    access_token = response['access_token']
    print response

    return jsonify(**jwt.decode(response['access_token'], verify=False))


def get_oauth_token():
    print 'access_token = ' + access_token
    return (access_token, '')


if __name__ == '__main__':
    app.debug = True

    open_edx_remote = oauth.remote_app(
        'college-board',
        request_token_url=None,
        # move URLs to configuration
        access_token_url='{}/oauth2/access_token/?token_type=jwt'.format(app.config['BASE_HOSTNAME']),
        authorize_url='{}/oauth2/authorize'.format(app.config['BASE_HOSTNAME']),
        consumer_key=app.config['CLIENT_ID'],
        consumer_secret=app.config['CLIENT_SECRET'],
        access_token_params={'token_type':'jwt'},
    )
    open_edx_remote._tokengetter = get_oauth_token

    app.add_url_rule('/login', view_func=login, methods=['GET'])
    app.add_url_rule('/redirect', view_func=redirect, methods=['GET'])

    import os
    # allow no SSL for debug/test environment
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

    app.run(host="0.0.0.0", port=5000, threaded=True)
