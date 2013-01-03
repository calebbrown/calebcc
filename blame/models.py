import os
import hashlib
import json
from glob import glob

from dictshield.document import Document as BaseDocument
from dictshield.fields import StringField, DateTimeField
from dictshield.fields.compound import ListField
from dateutil.parser import parse as date_parse

from .formats import get_formatter


class DocumentNotFound(Exception):
    pass


class DocumentIndexNotFound(Exception):
    pass


class DocumentViewNotFound(Exception):
    pass


class DocumentMoved(Exception):
    def __init__(self, location, *args, **kwargs):
        self.location=location
        super(DocumentMoved, self).__init__(*args, **kwargs)


class FuzzyDateTimeField(DateTimeField):
    def __set__(self, instance, value):
        if isinstance(value, (str, unicode)):
            value = FuzzyDateTimeField.parse_date(value)

        instance._data[self.field_name] = value

    @classmethod
    def parse_date(cls, value):
        return date_parse(value, ignoretz=True, dayfirst=True,
            yearfirst=True, fuzzy=True)


class Document(BaseDocument):
    type = StringField(required=True)

    path = StringField(required=True)

    redirect_path = StringField()

    title = StringField()
    body = StringField()
    format = StringField()

    authors = ListField(StringField())

    created_on = FuzzyDateTimeField()
    modified_on = FuzzyDateTimeField()
    publish_on = FuzzyDateTimeField()
    parsed_on = FuzzyDateTimeField()

    @property
    def key(self):
        return '%s/%s' % (self.type, self.path)

    @property
    def has_summary(self):
        return '<!--break-->' in self.body

    @property
    def summary(self):
        """
        Generate a summary from a longer post.

        This is done in one of two ways:
         1. Detecting a <!--break--> in the html.
         2. Automatically finding the end of a paragraph
        """

        if '<!--break-->' in self.body:
            return self.body.split('<!--break-->', 1)[0]

        return self.body

    @property
    def formatter(self):
        return get_formatter(self.format)

    def render_body(self):
        return self.formatter(self.body)

    def render_summary(self):
        return self.formatter(self.summary)

    def assign(self, field_name, value):
        if field_name not in self._fields:
            # Abort silently if we can't be set
            return

        field = self._fields[field_name]
        if isinstance(field, ListField):
            if not hasattr(self, field_name):
                setattr(self, field_name, [])
            getattr(self, field_name).append(value)
        else:
            setattr(self, field_name, value)

    def create_redirect(self, path):
        return self.__class__(
                path=path,
                redirect_path=self.path,
                type=self.type,
                format=self.format,
                created_on=self.created_on,
                parsed_on=self.parsed_on,
            )


class DocumentIterator(object):

    def __init__(self, manager, name=None, index=None):
        self.manager = manager
        self.name = name
        self.index = index
        if name:
            self.index = self.manager.index(name)

    def __len__(self):
        return len(self.index)

    def __getitem__(self, item):
        if isinstance(item, slice):
            return DocumentIterator(self.manager, index=self.index[item])
        else:
            return self.manager.get(self.index[item])

    def __iter__(self):
        for key in self.index:
            yield self.manager.get(key)

    def reverse(self):
        index = self.index[:]
        index.reverse()
        return self.__class__(self.manager, index=index)


class DocumentManager(object):

    def __init__(self, store_path, document_class=Document):
        self.store_path = store_path
        self.document_class = document_class

    def _pathname_for_key(self, key):
        filename = '%s.json' % hashlib.sha1(key.encode('ascii', 'ignore')).hexdigest()
        pathname = os.path.join(self.store_path, filename[0:2], filename[2:4],
            filename)
        return pathname

    def _pathname_for_index(self, index):
        filename = '%s.json' % hashlib.sha1(index.encode('ascii', 'ignore')).hexdigest()
        pathname = os.path.join(self.store_path, 'index', filename)
        return pathname

    def _pathname_for_view(self, view):
        filename = '%s.json' % hashlib.sha1(view.encode('ascii', 'ignore')).hexdigest()
        pathname = os.path.join(self.store_path, 'views', filename)
        return pathname

    def _create_path(self, pathname):
        path = os.path.dirname(pathname)

        if not os.path.exists(path):
            os.makedirs(path)

    def _load(self, pathname):
        with open(pathname, 'r') as fd:
            data = json.loads(fd.read())
            document = self.document_class(**data)

        return document

    def exists(self, key):
        pathname = self._pathname_for_key(key)
        return os.path.exists(pathname)

    def get(self, key):
        if not self.exists(key):
            raise DocumentNotFound()

        pathname = self._pathname_for_key(key)
        document = self._load(pathname)
        if document.redirect_path:
            raise DocumentMoved(location=document.redirect_path)
        return document

    def save(self, document):
        key = document.key
        json = self.document_class.make_json_ownersafe(document)

        pathname = self._pathname_for_key(key)
        self._create_path(pathname)

        with open(pathname, 'w') as fd:
            fd.write(json)

    def generate_index(self, filters={}, sort_field=None):
        files = glob(os.path.join(self.store_path, '??/??/*.json'))
        docs = []

        for f in files:
            doc = self._load(f)

            matches_filters = True
            for field, value in filters.iteritems():
                doc_value = getattr(doc, field, None)
                if isinstance(doc_value, list) and value in doc_value:
                    continue
                elif value == doc_value:
                    continue
                matches_filters = False
                break

            if matches_filters:
                docs.append(doc)

        if sort_field is not None:
            reverse = sort_field[0] == '-'
            sort_field = sort_field[1:] if reverse else sort_field
            sorted_docs = sorted(docs,
                key=lambda doc: getattr(doc, sort_field), reverse=reverse)
        else:
            sorted_docs = docs

        index = [doc.key for doc in sorted_docs]
        return index

    def create_index(self, name, filters={}, sort_field=None):
        index = self.generate_index(filters, sort_field)

        pathname = self._pathname_for_index(name)
        self._create_path(pathname)

        with open(pathname, 'w') as fd:
            fd.write(json.dumps(index))

    def index(self, name):
        pathname = self._pathname_for_index(name)

        if not os.path.exists(pathname):
            raise DocumentIndexNotFound()

        with open(pathname, 'r') as fd:
            index = json.loads(fd.read())

        return index

    def list(self, name):
        return DocumentIterator(self, name=name)

    def create_view(self, name, index_name, map_func=None, reduce_func=None,
            empty_result=None):

        result = empty_result if empty_result is not None else []

        if map_func is None:
            map_func = lambda x: x

        if reduce_func is None:
            reduce_func = lambda x, r: r + [x]

        for doc in self.list(index_name):
            map_generator = map_func(doc)
            for mapping in map_generator:
                result = reduce_func(mapping, result)

        pathname = self._pathname_for_view(name)
        self._create_path(pathname)

        with open(pathname, 'w') as fd:
            fd.write(json.dumps(result))

        return result

    def view(self, name):
        pathname = self._pathname_for_view(name)

        if not os.path.exists(pathname):
            raise DocumentViewNotFound()

        with open(pathname, 'r') as fd:
            view = json.loads(fd.read())

        return view



class CachedDocumentManager(DocumentManager):

    def __init__(self, store_path, cache, cache_ttl=300,
            document_class=Document):
        self.cache = cache
        self.cache_ttl = cache_ttl
        super(CachedDocumentManager, self).__init__(store_path,
            document_class=document_class)

    def _gen_cache_key(self, kind, value):
        return '%s:%s:%s' % (
                kind,
                hashlib.sha1(value).hexdigest(),
                hashlib.sha1(os.path.realpath(self.store_path)).hexdigest(),
            )

    def _gen_doc_key(self, pathname):
        return self._gen_cache_key('doc', pathname)

    def _gen_index_key(self, name):
        return self._gen_cache_key('index', name)

    def _gen_view_key(self, name):
        return self._gen_cache_key('view', name)

    def _cache_set(self, key, data):
        return self.cache.set(key, data, time=self.cache_ttl)

    def _cache_get(self, key):
        return self.cache.get(key)

    def _cache_delete(self, key):
        return self.cache.delete(key)

    def _load(self, pathname):
        ckey = self._gen_doc_key(pathname)
        cached_doc = self._cache_get(ckey)
        if cached_doc:
            return self.document_class(**json.loads(cached_doc))

        doc = super(CachedDocumentManager, self)._load(pathname)
        self._cache_set(ckey, doc.to_json())
        return doc

    def save(self, document):
        super(CachedDocumentManager, self).save(document)

        pathname = self._pathname_for_key(document.key)
        ckey = self._gen_doc_key(pathname)
        self._cache_delete(ckey)

    def create_index(self, name, filters={}, sort_field=None):
        super(CachedDocumentManager, self).create_index(name, filters=filters,
                sort_field=sort_field)
        ckey = self._gen_index_key(name)
        self._cache_delete(ckey)

    def index(self, name):
        ckey = self._gen_index_key(name)
        cached_index = self._cache_get(ckey)
        if cached_index:
            return json.loads(cached_index)

        index = super(CachedDocumentManager, self).index(name)
        self._cache_set(ckey, json.dumps(index))
        return index

    def view(self, name):
        ckey = self._gen_view_key(name)
        cached_view = self._cache_get(ckey)
        if cached_view:
            return json.loads(cached_view)

        view = super(CachedDocumentManager, self).view(name)
        self._cache_set(ckey, json.dumps(view))
        return view

    def create_view(self, name, index_name, map_func=None, reduce_func=None,
            empty_result=None):
        r = super(CachedDocumentManager, self).create_view(name,
            index_name, map_func=map_func,
            reduce_func=reduce_func, empty_result=empty_result)
        ckey = self._gen_view_key(name)
        self._cache_delete(ckey)
        return r
