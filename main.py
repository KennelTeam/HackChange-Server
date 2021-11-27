import random
import flask
from flask import g
from flask import request, jsonify

from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from sqlalchemy.sql.functions import user
from store.images import Comment, Instrument, Investor, Post, Subscription, Topic
from tokens import generate_access_token

import store

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
    if request.endpoint != 'login' and request.endpoint != 'register':
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


@app.route('/register')
def register():
    query_args = request.args
    if 'nickname' not in query_args or 'password' not in query_args:
        return jsonify({
            'ok': False,
            'error_code': 5,
            'error_desc': 'You must pass nickname and password'
        })

    nickname = query_args['nickname']
    password = query_args['password']

    db = store.get_session()
    if db.query(Investor).filter(Investor.nickname == nickname).first() is not None:
        return jsonify({
            'ok': False,
            'error_code': 4,
            'error_desc': 'User with this nickname already exists'
        })

    new_investor = Investor(nickname, password, generate_access_token())
    db.add(new_investor)
    new_investor = db.query(Investor).filter(
        Investor.nickname == nickname).first()

    response = jsonify({
        'ok': True,
        'user_id': new_investor.id,
        'access_token': new_investor.access_token
    })

    return response


@app.route('/login')
def login():
    query_args = request.args
    if 'nickname' not in query_args or 'password' not in query_args:
        return jsonify({
            'ok': False,
            'error_code': 5,
            'error_desc': 'You must pass nickname and password'
        })

    nickname = query_args['nickname']
    password = query_args['password']

    db = store.get_session()
    investor = db.query(store.Investor).filter(
        Investor.nickname == nickname).first()
    if investor is None:
        return jsonify({
            'ok': False,
            'error_code': 0,
            'error_desc': 'No user with this nickname'
        })

    if investor.password != password:
        return jsonify({
            'ok': False,
            'error_code': 1,
            'error_desc': 'Incorrect password'
        })

    return jsonify({
        'ok': True,
        'user_id': investor.id,
        'access_token': investor.access_token
    })


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
        'id': profile_id,
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
        nickname = query_args['nickname']
        if store.get_session().query(store.Investor).filter(Investor.nickname == nickname).first() is not None:
            return jsonify({
                'ok': False,
                'error_code': 7,
                'error_desc': 'This nickname is already taken'
            })
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

    session = store.get_session()
    post = session.query(Post).filter(Post.id == post_id).first()
    topic = session.query(Topic).filter(Topic.id == post.topic_id).first()
    author = session.query(Investor).filter(
        Investor.id == post.author_id).first()

    return jsonify({
        'ok': True,
        'id': post_id,
        'timestamp': post.timestamp,
        'topic': {
            'id': topic.id,
            'title': topic.title
        },
        'author': {
            'id': author.id,
            'nickname': author.nickname,
            'avatar_link': author.avatar_link
        },
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

    return jsonify({
        'ok': True,
        'instruments': mapped
    })


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

    topics = store.get_session().query(Topic).filter(
        Topic.instrument_id == instrument_id).all()
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

    session = store.get_session()
    posts = session.query(Post).filter(Post.topic_id == topic_id).all()

    mapped = []
    for post in posts:
        topic = session.query(Topic).filter(Topic.id == post.topic_id).first()
        author = session.query(Investor).filter(
            Investor.id == post.author_id).first()
        mapped.append({
            'id': post.id,
            'topic': {
                'id': topic.id,
                'title': topic.title
            },
            'author': {
                'id': author.id,
                'nickname': author.nickname,
                'avatar_link': author.avatar_link
            },
            'text': post.text,
            'timestamp': post.timestamp
        })

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


@app.route('/addComment')
def add_comment():
    query_args = request.args

    if 'post_id' or 'text' not in query_args:
        return jsonify({
            'ok': False,
            'error_code': 5,
            'error_desc': 'You must pass post_id and text'
        })

    post_id = query_args['post_id']
    text = query_args['text']

    store.get_session().add(Comment(post_id, g.me.id, text))

    return jsonify({
        'ok': True
    })


@app.route('/commentsByPost')
def comments_by_post():
    query_args = request.args

    if 'post_id' not in query_args:
        return jsonify({
            'ok': False,
            'error_code': 5,
            'error_desc': 'You must pass post_id'
        })

    post_id = query_args['post_id']

    session = store.get_session()
    comments = session.query(
        Comment).filter(Comment.post_id == post_id).all()

    mapped = []
    for comment in comments:
        commenter = session.query(Investor).filter(
            Investor.id == comment.commenter_id).first()
        mapped.append({
            'commenter': {
                'id': commenter.id,
                'nickname': commenter.nickname,
                'avatar_link': commenter.avatar_link
            },
            'text': comment.text,
            'timestamp': comment.timestamp
        })

    return jsonify({
        'ok': True,
        'comments': mapped
    })


@app.route('/subscribe')
def subscribe():
    query_args = request.args

    if 'blogger_id' not in query_args:
        return jsonify({
            'ok': False,
            'error_code': 5,
            'error_desc': 'You must pass blogger_id'
        })

    blogger_id = query_args['blogger_id']
    store.get_session().add(Subscription(g.me.id, blogger_id))

    return jsonify({
        'ok': True
    })


@app.route('/mySubscriptionsPosts')
def subs_posts():
    session = store.get_session()
    my_subs = session.query(Subscription).filter(
        Subscription.subscriber_id == g.me.id).all()
    my_subs_posts = []

    for my_sub in my_subs:
        cur_sub_posts = session.query(Post).filter(
            Post.author_id == my_sub.blogger_id).all()
        my_subs_posts += cur_sub_posts

    mapped = []
    for post in my_subs_posts:
        post: Post
        topic = session.query(Topic).filter(Topic.id == post.topic_id).first()
        author = session.query(Investor).filter(
            Investor.id == post.author_id).first()
        mapped.append({
            'id': post.id,
            'topic': {
                'id': topic.id,
                'title': topic.title
            },
            'author': {
                'id': author.id,
                'nickname': author.nickname,
                'avatar_link': author.avatar_link
            },
            'text': post.text,
            'timestamp': post.timestamp
        })

    return jsonify({
        'ok': True,
        'posts': mapped
    })


@app.route('/subscribersCount')
def subs_count():
    query_args = request.args

    if 'blogger_id' not in query_args:
        return jsonify({
            'ok': False,
            'error_code': 5,
            'error_desc': 'You must pass blogger_id'
        })

    blogger_id = query_args['blogger_id']

    all_subs = store.get_session().query(Subscription).filter(
        Subscription.blogger_id == blogger_id).all()

    return jsonify({
        'ok': True,
        'subs_count': len(all_subs)
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
