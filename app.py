from flask import Flask, render_template, request, redirect, abort
from uuid import uuid1 as uuid
from time import time, ctime
import redis

r = redis.Redis(host='redis', decode_responses=True)

app = Flask(__name__)


@app.route('/')
def index():
    sort_by_time = True
    if request.args.get('sort') == 'votes':
        sort_by_time = False
        articles_id = r.zrevrange('votes', 0, -1)
    else:
        articles_id = r.zrevrange('time', 0, -1)
    articles_title = []
    articles_votes = []
    articles_created = []
    for article_id in articles_id:
        articles_title.append(r.hget('article:'+article_id, 'title'))
        articles_votes.append(r.hget('article:'+article_id, 'votes'))
        created = r.hget('article:'+article_id, 'created')
        articles_created.append(ctime(int(created)))

    return render_template('index.html', ids=articles_id, titles=articles_title, votes=articles_votes, createds=articles_created, sort_by_time=sort_by_time)

@app.route('/article/<string:article_id>', methods=['GET', 'POST'])
def article(article_id):

    if not r.exists('article:'+article_id):
        abort(404)

    msg = None
    if request.method == 'POST':
        # 判断是否投过票
        poster = request.form['poster']
        if r.sismember('voted:'+article_id, poster):
            msg = '您已经投过票了!'
        else:
            msg = '投票成功'
            r.sadd('voted:'+article_id, poster)
            r.hincrby('article:'+article_id, 'votes')
            r.zincrby('votes', 1, article_id)

    title = r.hget('article:'+article_id, 'title')
    content = r.hget('article:'+article_id, 'content')
    created = r.hget('article:'+article_id, 'created')
    created = ctime(int(created))
    poster = r.hget('article:'+article_id, 'poster')
    votes = r.hget('article:'+article_id, 'votes')
    return render_template('article.html', title=title, content=content, created=created, poster=poster, votes=votes, msg=msg)


@app.route('/new', methods=['GET', 'POST'])
def new_article():
    # 新建文章
    if request.method == 'POST':
        article_id = uuid().hex
        article_title = request.form['title']
        article_content = request.form['content']
        article_poster = request.form['poster']
        article_created = int(time())

        r.zadd('time', {article_id: article_created})
        r.zadd('votes', {article_id: 0})
        r.hset('article:'+article_id, 'title', article_title)
        r.hset('article:'+article_id, 'content', article_content)
        r.hset('article:'+article_id, 'created', article_created)
        r.hset('article:'+article_id, 'poster', article_poster)
        r.hset('article:'+article_id, 'votes', 0)

        return redirect('/')

    return render_template('new.html')
