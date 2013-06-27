
from dictshield.fields import StringField
from dictshield.fields.compound import ListField

from blame.models import (DocumentNotFound, DocumentMoved,
    CachedDocumentManager, Document)

from . import config


## Custom document model for our special changes
class MyDocument(Document):
    channels = ListField(StringField())
    series = ListField(StringField())

## Create an instance of the manager we use to look after our documents
manager = CachedDocumentManager(config.DATA_STORE, config.CACHE,
    cache_ttl=3600, document_class=MyDocument)
