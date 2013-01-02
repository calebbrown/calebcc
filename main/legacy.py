from bottle import (redirect, response, abort)

from feedgenerator import DefaultFeed as Feed

from . import config
from models import (DocumentNotFound, DocumentMoved, manager)


def home_redirect(junk=None):
    """
    Legacy redirect for old Drupal search urls
    """
    redirect('/')


def tag_redirect(name):
    """
    Legacy redirect for tags.

    Based on traffic it redirects to the page represented by
    the most popular tags
    """
    if name in ['emoticon', 'chat', 'facebook', 'smilie', 'list']:
        redirect('/blog/complete-list-facebook-chat-emoticons')
    elif name == 'contact':
        redirect('/feedback')
    redirect('/blog')


def node_redirect(node_id):
    for doctype, redirbase in {'blog':'/blog/', 'page':'/'}.items():
        try:
            doc = manager.get('%s/node/%s' % (doctype, node_id))
        except DocumentNotFound, e:
            doc = None
        except DocumentMoved, e:
            redirect(redirbase + e.location)
        if doc:
            redirect(redirbase + doc.path)
    abort(404)


def removed_feed():
    """
    Legacy feed for Drupal comment feed

    Adds a single entry indicating the feed is no longer in use.
    """
    title = '%s: Deprecated Feed' % config.SITE_NAME
    description = 'This feed has been deprecated and no longer exists.'
    feed_url = config.SITE_BASE + 'crss'
    feed = Feed(title, config.SITE_BASE, description, feed_url=feed_url,
        feed_guid=feed_url, feed_copyright=u'(c) Copyright 2012, Caleb Brown')
    feed.add_item('This RSS feed no longer exists', config.SITE_BASE,
        'This feed no longer exists. But calebbrown.id.au is still '
        'alive and kicking. Please visit the hompage to see what\'s new.')
    response.content_type = 'application/rss+xml; charset=utf-8'
    return feed.writeString('utf-8')


def add_views(app):
    app.route('/search/node<junk:re:.*>', callback=home_redirect)
    app.route('/crss', callback=removed_feed)
    app.route('/tag/<name>', callback=tag_redirect)
    app.route('/node/<node_id>', callback=node_redirect)
