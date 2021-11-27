import random
import flask
from flask import g
from flask import request, jsonify

from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from sqlalchemy.sql.functions import user
from store.images import Instrument, Investor, Post, Topic
from tokens import generate_access_token

import store


GOOGLE_CLIENT_ID = '452745278337-csmmksfrl50qq33j37r2rg9900v245k5.apps.googleusercontent.com'

app = flask.Flask(__name__)
app.config['DEBUG'] = True




def investor_by_token(token: str) -> bool:
    session = store.get_session()
    investor = session.query(store.Investor).filter(
        store.Investor.access_token == token).first()

    return investor


@app.before_request
def access_token_checker():
    query_args = request.args
    if request.endpoint != 'authent':
        if 'access_token' not in query_args:
            return jsonify({
                'ok': False,
                'error_code': 2,
                'error_desc': 'No access token passed'
            })

        access_token = query_args['access_token']
        investor = investor_by_token(access_token)
        if investor is None:
            return jsonify({
                'ok': False,
                'error_code': 3,
                'error_desc': 'Invalid access token'
            })

        g.me = investor


@app.after_request
def save_db(response):
    store.commit()
    store.clear_session()
    return response


def verify_google_token(token: str) -> str:
    google_id_info = {}

    try:
        google_id_info = id_token.verify_oauth2_token(
            token, google_requests.Request(), GOOGLE_CLIENT_ID)
    except Exception as e:
        return None

    return str(google_id_info['sub'])


def dummy_google_token(token: str) -> str:
    return random.choice(['115989421480695081793'])


@app.route('/authent')
def authent():
    query_args = request.args
    if 'google_token' not in query_args:
        return jsonify({
            'ok': False,
            'error_code': 4,
            'error_desc': 'No google token passed'
        })
    investor_id = dummy_google_token(query_args['google_token'])

    if investor_id is None:
        return jsonify({
            'ok': False,
            'error_code': 1,
            'error_desc': 'Incorrect google token'
        })

    db = store.get_session()
    investor = db.query(store.Investor).filter_by(
        google_user_id=investor_id).first()

    if investor is None:
        investor = store.Investor(investor_id, generate_access_token())
        db.add(investor)

    response = jsonify({
        'ok': True,
        'user_id': investor.id,
        'access_token': investor.access_token
    })

    return response


@app.route('/getProfile')
def user_profile():
    query_args = request.args
    if 'profile_id' not in query_args:
        return jsonify({
            'ok': False,
            'error_code': 5,
            'error_desc': 'Requested profile id is not specified'
        })

    profile_id = query_args['profile_id']

    session = store.get_session()
    req_investor = session.query(Investor).filter(
        Investor.id == profile_id).first()
    if req_investor is None:
        return jsonify({
            'ok': False,
            'error_code': 5,
            'error_desc': 'No user with such id'
        })
    if req_investor.nickname is None:
        return jsonify({
            'ok': False,
            'error_code': 5,
            'error_desc': 'No user with such id'
        })

    posts_ids = list(map(lambda post: post.id, session.query(
        Post).filter(Post.author_id == profile_id)))

    return jsonify({
        'ok': True,
        'info': {
            'nickname': req_investor.nickname,
            'avatar_link': req_investor.avatar_link
        },
        'posts': posts_ids
    })


@app.route('/setMyInfo')
def set_my_info():
    query_args = request.args
    investor: Investor = g.me

    if 'nickname' in query_args:
        investor.nickname = query_args['nickname']

    if 'avatar_link' in query_args:
        investor.avatar_link = query_args['avatar_link']

    return jsonify({
        'ok': True
    })


@app.route('/getPost')
def get_post():
    query_args = request.args
    if 'post_id' not in query_args:
        return jsonify({
            'ok': False,
            'error_code': 5,
            'error_desc': 'post_id is not passed'
        })

    post_id = query_args['post_id']

    post = store.get_session().query(Post).filter(Post.id == post_id).first()
    return jsonify({
        'ok': True,
        'instrument_id': post.topic_id,
        'author_id': post.author_id,
        'text': post.text
    })


@app.route('/allInstruments')
def all_instruments():
    instruments = store.get_session().query(Instrument).all()

    mapped = list(map(lambda instr: {
        'id': instr.id,
        'name': instr.name,
        'details': instr.details
    }, instruments))

    return jsonify(mapped)

@app.route('/addTopic')
def add_topic():
    query_args = request.args

    if 'instrument_id' not in query_args or 'title' not in query_args:
        return jsonify({
            'ok': False,
            'error_code': 5,
            'error_desc': 'You must pass instrument_id and title'
        })

    instrument_id = query_args['instrument_id']
    title = query_args['title']

    session = store.get_session()
    if session.query(Instrument).filter(Instrument.id == instrument_id).first() is None:
        return jsonify({
            'ok': False,
            'error_code': 6,
            'error_desc': 'Instruments with such id doesn\'t exist'
        })
    
    session.add(Topic(instrument_id, title))

    return jsonify({
        'ok': True
    })

@app.route('/topicsByInstrument')
def topics_by_instrument():
    query_args = request.args

    if 'instrument_id' not in query_args:
        return jsonify({
            'ok': False,
            'error_code': 5,
            'error_desc': 'instrument_id is not passed'
        })

    instrument_id = query_args['instrument_id']

    topics = store.get_session().query(Topic).filter(Topic.instrument_id == instrument_id).all()
    mapped = list(map(lambda topic: {
        'id': topic.id,
        'title': topic.title
    }, topics))

    return jsonify({
        'ok': True,
        'topics': mapped
    })

@app.route('/postsByTopic')
def posts_by_topic():
    query_args = request.args

    if 'topic_id' not in query_args:
        return jsonify({
            'ok': False,
            'error_code': 5,
            'error_desc': 'topic_id is not passed'
        })

    topic_id = query_args['topic_id']

    posts = store.get_session().query(Post).filter(
        Post.topic_id == topic_id).all()
    mapped = list(map(lambda post: {
        'instrument_id': post.topic_id,
        'author_id': post.author_id,
        'text': post.text
    }, posts))

    return jsonify({
        'ok': True,
        'posts': mapped
    })

@app.route('/addPost')
def add_post():
    query_args = request.args

    if 'topic_id' not in query_args or 'text' not in query_args:
        return jsonify({
            'ok': False,
            'error_code': 5,
            'error_desc': 'You must pass topic_id and text'
        })

    topic_id = query_args['topic_id']
    text = query_args['text']

    store.get_session().add(Post(g.me.id, topic_id, text))

    return jsonify({
        'ok': True
    })

app.run(host='0.0.0.0', port=8080)