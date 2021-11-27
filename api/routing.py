import flask
from flask import request, jsonify

from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from api.tokens import generate_access_token

import store


# def requires_token(func):
#     def wrapper(*args, **kwargs):
#         query_args = request.args

#         func()

GOOGLE_CLIENT_ID = 'http://452745278337-csmmksfrl50qq33j37r2rg9900v245k5.apps.googleusercontent.com'

app = flask.Flask(__name__)
app.config['DEBUG'] = True


@app.route('/authent')
def r():
    query_args = request.args
    google_id_info = {}

    try:
        google_id_info = id_token.verify_oauth2_token(
            query_args['google_token'], google_requests.Request(), GOOGLE_CLIENT_ID)
    except Exception as e:
        raise e

    if google_id_info == {}:
        return jsonify({
            'ok': False,
            'error_code': 1,
            'error_desc': 'Google token has incorrect format'
        })

    if not google_id_info['email_verified']:
        return jsonify({
            'ok': False,
            'error_code': 2,
            'error_desc': 'Email not verified'
        })

    db = store.get_session()
    investor = db.query(store.Investor).filter(
        store.Investor.email == google_id_info['email']).first()
    if not investor:
        investor = store.Investor(google_id_info['email'])
        db.add(investor)

    if not investor.access_token:
        investor.access_token = generate_access_token()

    db.commit()
    store.clear_session()

    return jsonify({
        'ok': True,
        'access_token': investor.access_token
    })


@app.route('/userProfile')
def userProfile():
    query_args = request.args


app.run()
