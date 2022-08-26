import numpy as np
import toml
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

db = SQLAlchemy(app)
app.config.from_file('config.toml', load=toml.load)


class all_likes(db.Model):
    __tablename__ = 'collect'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    article_id = db.Column(db.String(40))
    user_id = db.Column(db.String(40))


def user_sim_recommend_score(pre_userid):
    def euclidean_distance(user1access, user2access):
        both_rated_num = 0
        for item in user1access:
            if item in user2access:
                both_rated_num += 1
        if both_rated_num == 0:
            return 0  #

        squared_difference = []
        for item in user1access:
            if item in user2access:
                squared_difference.append(np.square(user1access[item] - user2access[item]))
        return 1 / (1 + np.sqrt(np.sum(squared_difference)))

    likes = all_likes.query.filter().all()
    user_dict = {}
    for every_like in likes:
        try:
            user_dict[every_like.user_id][every_like.article_id] = 1
        except:
            user_dict[every_like.user_id] = {}
            user_dict[every_like.user_id][every_like.article_id] = 1
    user_list = user_dict.keys()
    every_user = pre_userid
    max = 0
    like_best = None
    for another_user in user_list:
        if every_user == another_user:
            continue
        t = euclidean_distance(user_dict[every_user], user_dict[another_user])
        if t > max:
            max = t
            like_best = another_user
    try:
        return list(user_dict[like_best].keys())
    except:
        t = []
        return t
