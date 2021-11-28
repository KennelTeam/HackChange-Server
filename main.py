
import os
import random
import flask
from flask import g
from flask import request, jsonify
from flask.helpers import flash, send_from_directory, url_for

from sqlalchemy.sql.functions import user
from werkzeug.datastructures import FileStorage
from werkzeug.utils import redirect, send_file
from store.images import Comment, Instrument, Investor, Post, PostVoting, Subscription, Topic
from tokens import generate_access_token, generate_avatar_id
from PIL import Image

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


@app.route('/uploadAvatar', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({
            'ok': False,
            'error_code': 8,
            'error_desc': 'No file passed'
        })
    file = request.files['file']
    if file.filename.split('.')[-1] not in ['jpg', 'png']:
        return jsonify({
            'ok': False,
            'error_code': 11,
            'error_desc': 'Incorrect format. Avatars can be JPG or PNG'
        })

    if g.me.avatar_link is None:
        g.me.avatar_link = generate_avatar_id(g.me.id)

    temp = 'temp/' + file.filename
    file.save(temp)
    Image.open(temp).save('avatars/' + g.me.avatar_link)
    os.remove(temp)

    return jsonify({
        'ok': True
    })

@app.route('/getAvatar')
def download_my_avatar():
    query_args = request.args

    if 'user_id' not in query_args:
        return jsonify({
            'ok': False,
            'error_code': 5,
            'error_desc': 'You must pass user_id'
        })

    user_id = query_args['user_id']

    user = store.get_session().query(Investor).filter(Investor.id == user_id).first()
    if user is None:
        return jsonify({
            'ok': False,
            'error_code': 10,
            'error_desc': 'User with requested id doesn not exist'
        })

    return send_from_directory(directory='avatars/', path=user.avatar_link)


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

    new_investor = Investor(nickname, password)
    db.add(new_investor)
    new_investor = db.query(Investor).filter(
        Investor.nickname == nickname).first()
    new_investor.access_token = generate_access_token(new_investor.id)
    new_investor.avatar_link = generate_avatar_id(new_investor.id)

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
    if 'user_id' not in query_args:
        return jsonify({
            'ok': False,
            'error_code': 5,
            'error_desc': 'You must specify user_id'
        })

    profile_id = query_args['user_id']

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

    subs_of_profile = session.query(Subscription).filter(
        Subscription.blogger_id == req_investor.id)
    
    am_i_subscribed = subs_of_profile.filter(Subscription.subscriber_id == g.me.id).first() is not None

    return jsonify({
        'ok': True,
        'am_i_subscribed': am_i_subscribed,
        'subscribers_count': len(subs_of_profile.all()),
        'info': {
            'user_id': profile_id,
            'nickname': req_investor.nickname,
        },
        'posts': posts_ids
    })


@app.route('/setMyInfo')
def set_my_info():
    query_args = request.args
    investor: Investor = g.me

    if 'nickname' not in query_args:
        return jsonify({
            'ok': False,
            'error_code': 5,
            'error_desc': 'You mus pass nickname'
        })

    nickname = query_args['nickname']
    if store.get_session().query(store.Investor).filter(Investor.nickname == nickname).first() is not None:
        return jsonify({
            'ok': False,
            'error_code': 7,
            'error_desc': 'This nickname is already taken'
        })
    investor.nickname = query_args['nickname']

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
    votes_all = session.query(PostVoting).filter(PostVoting.post_id == post.id)
    votes_count = len(votes_all.filter(PostVoting.up_voted == True).all(
    )) - len(votes_all.filter(PostVoting.up_voted == False).all())

    return jsonify({
        'ok': True,
        'post_id': post_id,
        'votes_count': votes_count,
        'timestamp': post.timestamp,
        'topic': {
            'topic_id': topic.id,
            'title': topic.title
        },
        'author': {
            'user_id': author.id,
            'nickname': author.nickname,
        },
        'text': post.text
    })


@app.route('/allInstruments')
def all_instruments():
    instruments = store.get_session().query(Instrument).all()

    mapped = list(map(lambda instr: {
        'instrument_id': instr.id,
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
        'topic_id': topic.id,
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
        votes_all = session.query(PostVoting).filter(
            PostVoting.post_id == post.id)
        votes_count = len(votes_all.filter(PostVoting.up_voted == True).all(
        )) - len(votes_all.filter(PostVoting.up_voted == False).all())


        mapped.append({
            'post_id': post.id,
            'votes_count': votes_count,
            'topic': {
                'topic_id': topic.id,
                'title': topic.title
            },
            'author': {
                'user_id': author.id,
                'nickname': author.nickname,
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

    if 'post_id' not in query_args or 'text' not in query_args:
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
                'user_id': commenter.id,
                'nickname': commenter.nickname,
            },
            'comment_id': comment.id,
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

    if 'user_id' not in query_args:
        return jsonify({
            'ok': False,
            'error_code': 5,
            'error_desc': 'You must pass user_id'
        })

    blogger_id = query_args['user_id']
    store.get_session().add(Subscription(g.me.id, blogger_id))

    return jsonify({
        'ok': True
    })


@app.route('/unsubscribe')
def unsubscribe():
    query_args = request.args

    if 'user_id' not in query_args:
        return jsonify({
            'ok': False,
            'error_code': 5,
            'error_desc': 'You must pass user_id'
        })

    blogger_id = query_args['user_id']

    session = store.get_session()
    session.delete(session.query(Subscription).filter(
        Subscription.subscriber_id == g.me.id and Subscription.blogger_id == blogger_id).first())

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
        votes_all = session.query(PostVoting).filter(PostVoting.post_id == post.id)
        votes_count = len(votes_all.filter(PostVoting.up_voted == True).all(
        )) - len(votes_all.filter(PostVoting.up_voted == False).all())
        mapped.append({
            'post_id': post.id,
            'votes_count': votes_count,
            'topic': {
                'topic_id': topic.id,
                'title': topic.title
            },
            'author': {
                'user_id': author.id,
                'nickname': author.nickname,
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

    if 'user_id' not in query_args:
        return jsonify({
            'ok': False,
            'error_code': 5,
            'error_desc': 'You must pass user_id'
        })

    blogger_id = query_args['user_id']

    all_subs = store.get_session().query(Subscription).filter(
        Subscription.blogger_id == blogger_id).all()

    return jsonify({
        'ok': True,
        'subs_count': len(all_subs)
    })

def modify_votes(up_voted: bool):
    query_args = request.args

    if 'post_id' not in query_args:
        return jsonify({
            'ok': False,
            'error_code': 5,
            'error_desc': 'You must pass user_id'
        })

    post_id = query_args['post_id']

    store.get_session().add(PostVoting(post_id, g.me.id, up_voted))
    

@app.route('/upvotePost')
def upvote_post():
    return modify_votes(True)

@app.route('/downvotePost')
def downvote_post():
    return modify_votes(False)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
