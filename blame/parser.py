import os
import glob
import datetime
import email.parser
import codecs

from .formats import format_for_extension, UnknownExtension


def gather_files(path, recursive=False):
    gathered_files = []

    files = glob.glob(os.path.join(path, '*'))
    while files:
        f = files.pop(0)
        if os.path.isdir(f):
            if recursive:
                files += glob.glob(os.path.join(f, '*'))
        else:
            gathered_files.append(f.replace(path, '').lstrip('/'))

    return gathered_files


def email_to_dict(file_descriptor):
    message = email.parser.Parser().parse(file_descriptor)

    # body
    email_dict = { 'body': [ message.get_payload() ] }

    # headers
    for (key, value) in message.items():
        key = key.lower() # lowercase them all to make for easy comparison
        if key not in email_dict:
            email_dict[key] = []
        email_dict[key].append(value)

    return email_dict


class Parser(object):

    def __init__(self, manager, **global_defaults):
        self.manager = manager
        self.defaults = global_defaults
        self._header_map = {
            'author': 'authors',
            'date': 'created_on',
            'created-date': 'created_on',
            'publish-date': 'publish_on',
        }

    def _create_doc(self, **extra):
        data = dict(self.defaults)
        data.update(extra)
        return self.manager.document_class(**data)

    def map_header_to_field(self, **extra):
        self._header_map.update(extra)

    def parse(self, source_path, recursive=False, **defaults):
        self.parse_folder(source_path, recursive=recursive, **defaults)

    def parse_folder(self, path, recursive=False, **defaults):
        path = os.path.abspath(path)

        # get all the files that are candidates for parsing
        files = gather_files(path, recursive=recursive)

        # filter all the filters that haven't changed
        # files = self.filter_files(path, files, last_run=FOOBAR)

        for file in files:
            self.parse_file(path, file, **defaults)

    def parse_file(self, path, filepath, **defaults):
        doc = self._create_doc(**defaults)
        self.build_document(path, filepath, doc)
        self.manager.save(doc)

    def build_document(self, path, filepath, doc):
        self.load_file_info(path, filepath, doc)
        self.load_file_content(path, filepath, doc)

    def load_file_info(self, path, filepath, doc):
        mtime = os.path.getmtime(os.path.join(path, filepath))
        mod_dt = datetime.datetime.fromtimestamp(mtime)

        (doc_path, ext) = os.path.splitext(filepath)

        doc.path = doc_path
        doc.created_on = mod_dt
        doc.modified_on = mod_dt
        doc.publish_on = mod_dt

        try:
            doc.format = format_for_extension(ext)
        except UnknownExtension:
            pass

    def load_file_content(self, path, filepath, doc):
        with codecs.open(os.path.join(path, filepath), mode='r', encoding='utf-8') as fd:
            data = email_to_dict(fd)

        # Grab any alternate slugs
        alts = data.pop('alt-slug', [])

        # Populate the document
        for (field, values) in data.iteritems():
            for value in values:
                doc.assign(self._header_map.get(field, field), value)

        # Create the redirects
        for alt in alts:
            redirect_doc = doc.create_redirect(alt)
            self.manager.save(redirect_doc)
