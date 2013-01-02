import datetime
import random
import os

from bottle import (Bottle, abort, redirect, TEMPLATE_PATH, static_file,
    response)
from bottle import jinja2_template as template

from feedgenerator import DefaultFeed as Feed

from . import config
from . import legacy
from models import (DocumentNotFound, DocumentMoved, manager)

__all__ = ['app']

app = Bottle()

# Arguments to send to every template we render
view_kwargs = {
    'STATIC_URL': '/static/',
    'SITE_BASE': config.SITE_BASE,
    'SITE_NAME': config.SITE_NAME,
    'NOW': datetime.datetime.now(),
    'ADVERT_LIMIT': datetime.datetime.now() - datetime.timedelta(config.ADVERT_LIMIT)
}
TEMPLATE_PATH += config.TEMPLATE_PATHS


try:
    from version import DEPLOY_VERSION
    view_kwargs['STATIC_URL'] = '/static/%s/' % DEPLOY_VERSION
except ImportError:
    pass


legacy.add_views(app)

@app.route('/favicon.ico')
def favicon():
    """
    Handle the favicon.ico responses.

    Eventually this will redirect to an icon in the static files.
    """
    abort(404, "Not Found")


@app.route('/')
def index():
    """
    Render the homepage.
    """
    page = config.CACHE.get('view:index')
    if page:
        return page

    docs = manager.list('blog')[:4]
    page = template('index.html', docs=docs, **view_kwargs)

    config.CACHE.set('view:index', page, time=300)
    return page


@app.route('/static/<path:path>')
def callback(path):
    """
    Debug view for serving up static files
    """
    if path.startswith('media/'):
        return static_file(path, root=config.DATA_SOURCE)
    return static_file(path, root=os.path.join(config.PROJECT_PATH, 'static'))


@app.route('/feed')
@app.route('/feed/channel/<name>')
def blog_feed(name='list_all'):
    """
    Feed generation for the blog
    """
    index_name = 'blog' if name == 'list_all' else 'blog_%s' % name
    docs = manager.list(index_name)[:20]

    channel_name = 'All' if name == 'list_all' else name.title()
    title = "%s: %s Blog Posts" % (config.SITE_NAME, channel_name)
    description = title
    feed_url = config.SITE_BASE + 'feed' + ('' if name == 'list_all' else '/channel/' + name)

    feed = Feed(title, config.SITE_BASE, description, feed_url=feed_url,
        feed_guid=feed_url, feed_copyright=u'(c) Copyright 2012, Caleb Brown')

    for doc in docs:
        feed.add_item(doc.title, config.SITE_BASE + 'blog/' + doc.path,
            doc.render_body(), pubdate=doc.publish_on,
            unique_id='blog/' + doc.path)

    response.content_type = 'application/rss+xml; charset=utf-8'
    return feed.writeString('utf-8')


@app.route('/blog')
@app.route('/blog/channel/<name>')
def blog_list(name='list_all'):
    """
    Blog index page

    Generates a list of posts in the blog. It can be filtered by channel.
    """
    page = config.CACHE.get('view:blog_list:%s' % name)
    if page:
        return page

    index_name = 'blog' if name == 'list_all' else 'blog_%s' % name
    docs = manager.list(index_name)
    page = template('list.html', docs=docs, channel=name, **view_kwargs)

    config.CACHE.set('view:blog_list:%s' % name, page, time=300)
    return page


@app.route('/blog/<path:re:[a-z0-9._/-]+>')
def blog_post(path):
    """
    Blog detail page

    Renders a single blog post.
    """
    newpath = path.strip('/')
    if path != newpath:
        redirect('/blog/' + newpath)

    try:
        doc = manager.get('blog/%s' % path)
    except DocumentNotFound, e:
        abort(404)
    except DocumentMoved, e:
        redirect('/blog/' + e.location)

    docs = manager.list('blog')
    last_index = len(docs) - 1
    index = manager.index('blog').index('blog/%s' % path)
    prev = docs[index+1] if index < last_index else None
    next = docs[index-1] if index > 0 else None

    view_context = {
        'doc': doc,
        'latest': docs[0],
        'random': docs[random.randint(0, last_index)],
        'next': next,
        'prev': prev,
    }
    view_context.update(view_kwargs)

    return template('document.html', **view_context)


@app.route('/<path:re:[a-z0-9._/-]+>')
def page(path):
    """
    Page detail page

    Renders a single page.
    """
    newpath = path.strip('/')
    if path != newpath:
        redirect(newpath)

    try:
        doc = manager.get('page/%s' % path)
    except DocumentNotFound, e:
        abort(404)
    except DocumentMoved, e:
         redirect('/' + e.location)

    view_context = {
        'doc': doc,
    }
    view_context.update(view_kwargs)

    return template('document.html', **view_context)


@app.error(404)
def error404(error):
    """
    404 Not Found handler

    Overrides the default response to keep users on the blog.
    """
    view_context = {}
    view_context.update(view_kwargs)
    return template('404.html', **view_context)
