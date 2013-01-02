
class UnknownFormat(Exception):
    pass


class UnknownExtension(Exception):
    pass


EXTENSION_FORMATS = {
    'html': 'html',
    'text': 'text',
    'txt': 'text',
    'md': 'markdown',
    'mdown': 'markdown',
    'markdown': 'markdown',
}

FORMATS = {
    'html': lambda text: text,
    'text': lambda text: text.replace('\n', '<br />\n'),
}


try:
    import markdown
    FORMATS['markdown'] = lambda text: markdown.markdown(text, ['extra'])
except ImportError:
    pass


def get_formatter(format):
    format = format.lower()
    if format not in FORMATS:
        raise UnknownFormat("Could not find a formatter for '%s'" % format)

    return FORMATS[format]


def format_for_extension(ext):
    ext = ext.lower()
    if ext not in EXTENSION_FORMATS:
        raise UnknownExtension("Could not find a format for extension '%s'" % ext)

    return EXTENSION_FORMATS[ext]
