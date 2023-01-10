from coopapi.apiShell import ApiShell
from coopapi.http_request_handlers import findRequestCallback, \
    createRequestCallback, \
    deleteRequestCallback, \
    updateRequestCallback, \
    jsonRequestCallback, \
    listRequestCallback
from coopapi.errors import DuplicateException, NotFoundException