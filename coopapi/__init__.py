from coopapi.apiShell import ApiShell
from coopapi.http_request_handlers import getOneRequestCallback, \
    postRequestCallback, \
    deleteRequestCallback, \
    putRequestCallback, \
    jsonRequestCallback, \
    getManyRequestCallback
from coopapi.errors import DuplicateException, NotFoundException