import os
from optparse import OptionParser

import blame

from . import config
from .models import manager


def parse(source_path=None, destination_path=None):
    """
    Parses the source documents and creates the JSON database for the site.

    It parses files in the `blog` and `legacy` directories and places them in
    the `blog` type.

    It parses files in the `pages` directory and places them in the
    `page` type.

    It creates a series of indexes for each channel option.

    It uses map-reduce to build a view for representing series and builds
    indexes from those.
    """
    if source_path is None:
        source_path = config.DATA_SOURCE
    if destination_path is not None:
        manager.store_path = destination_path

    path_fixer = lambda p: os.path.join(source_path, p)
    base_filters = {'type': 'blog', 'redirect_path': None}

    # create and setup the parser ready for input
    parser = blame.Parser(manager, format=config.DEFAULT_FORMAT)
    parser.map_header_to_field(channel='channels', series='series')

    # parse the content in the different paths
    parser.parse(path_fixer('blog'), type='blog')
    parser.parse(path_fixer('legacy'), type='blog')
    parser.parse(path_fixer('pages'), recursive=True, type='page')

    # create an index for all the blog entries so we can show a list of them
    manager.create_index('blog', filters=base_filters, sort_field='-created_on')

    # create indexes for each channel as well
    for (channel, value) in config.CHANNEL_OPTIONS:
        manager.create_index(
            'blog_%s' % channel,
            filters=dict([('channels', channel)] + base_filters.items()),
            sort_field='-created_on')

    # Series extraction and indexing
    #
    # This code below does two things:
    # 1. Goes through every blog post and extracts the name of each "Series".
    #    This is done using a simplistic form of map-reduce.
    # 2. for each series it finds creates and index for it

    def series_map(d):
        for s in d.series:
            yield s
    def series_reduce(d, r):
        if d not in r:
            r.append(d)
        return r

    # create a view containing all the series so we can link them together
    series_list = manager.create_view('blog_series', 'blog', map_func=series_map,
        reduce_func=series_reduce)

    # create an index for each series so we can list each post in it
    for series in series_list:
        manager.create_index(
            'blog_series_%s' % series,
            filters=dict([('series', series)] + base_filters.items()),
            sort_field='-created_on')


def run():
    """
    Method that can be run from the command line to parse documents
    """
    parser = OptionParser(usage="usage: %prog [options]")
    parser.add_option(
        "-s", "--source",
        action="store", type="string", dest="source_path")
    parser.add_option(
        "-d", "--dest", "--destination",
        action="store", type="string", dest="destination_path")
    (options, args) = parser.parse_args()

    parse(source_path=options.source_path,
        destination_path=options.destination_path)


if __name__ == '__main__':
    run()
