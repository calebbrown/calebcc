"""
Django's Feed Generator as a independent module.
"""


from base import SyndicationFeed
from feeds import Atom1Feed, Rss201rev2Feed, RssUserland091Feed, RssFeed

# This isolates the decision of what the system default is, so calling code can
# do "feedgenerator.DefaultFeed" instead of "feedgenerator.Rss201rev2Feed".
DefaultFeed = Rss201rev2Feed
