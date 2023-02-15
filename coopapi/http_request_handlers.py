from coopapi import errors as errors
import logging
from fastapi import Request, HTTPException, status
from typing import List, Dict, Callable, TypeVar, Optional
import pydantic
from starlette.responses import RedirectResponse
from cooptools.coopEnum import CoopEnum

logger = logging.getLogger('HTTPHandler')

T = TypeVar('T')

postRequestCallback = Callable[[Request, T], T]
getManyRequestCallback = Callable[[Request, Optional[Dict], Optional[int]], List[T]]
getOneRequestCallback = Callable[[Request, str], T]
putRequestCallback = Callable[[Request, str, Dict], T]
deleteRequestCallback = Callable[[Request, str], bool]
jsonRequestCallback = Callable[[Request, str], T]


class RequestType(CoopEnum):
    POST = 'POST'
    GET = 'GET'
    DELETE = 'DELETE'
    PUT = 'PUT'

def post_request_handler(request: Request, item: T, on_post_callback: postRequestCallback) -> T:
    code = None
    msg = None
    er = None

    try:
        ret = on_post_callback(request, item)
        logger.info(f"Creation Successful for item {item}")

        if type(ret) != type(item):
            raise TypeError(f"The on_create_callback method did not return the correct type")

        return ret
    except pydantic.error_wrappers.ValidationError as e:
        code = status.HTTP_400_BAD_REQUEST
        msg = f"Malformed json could not be interpreted as [{type(item).__name__}]: {e}"
        er = e
    except errors.DuplicateException as e:
        code = status.HTTP_409_CONFLICT
        msg = f"Record [{type(item).__name__}] already exists with id '{item.id}'. {e}"
        er = e
    except Exception as e:
        code = status.HTTP_500_INTERNAL_SERVER_ERROR
        msg = f"Unhandled error [{type(e)}]: {e}"
        er = e
    finally:
        if code is not None or msg is not None:
            logger.error(msg)
            raise HTTPException(status_code=code,
                                detail=msg) from er


def getmany_request_handler(request: Request, on_getmany_callback: getManyRequestCallback, query: Dict = None, limit: int = None) -> List[T]:
    code = None
    msg = None
    er = None

    try:
        return on_getmany_callback(request, query, limit)
    except Exception as e:
        code = status.HTTP_500_INTERNAL_SERVER_ERROR
        msg = f"Unhandled error [{type(e)}]: {e}"
        er = e
    finally:
        if code is not None or msg is not None:
            logger.error(msg)
            raise HTTPException(status_code=code,
                                detail=msg) from er


def getone_request_handler(id: str, request: Request, obj_type: type, on_getone_callback: getOneRequestCallback) -> List[T]:
    code = None
    msg = None

    try:
        return on_getone_callback(request, id)
    except errors.NotFoundException as e:
        code = status.HTTP_404_NOT_FOUND
        msg = f"{obj_type.__name__} with ID {id} not found. {e}"
    except Exception as e:
        code = status.HTTP_500_INTERNAL_SERVER_ERROR
        msg = f"Unhandled error [{type(e)}]: {e}"
    finally:
        if code is not None or msg is not None:
            logger.error(msg)
            raise HTTPException(status_code=code,
                                detail=msg)


def put_request_handler(request: Request, id: str, update_values: Dict, obj_type: type, on_put_callback: putRequestCallback):
    try:
        updated_item = on_put_callback(request, id, update_values)
        logger.info(f"Update Successful for item {updated_item} with new values {update_values}")
        return updated_item
    except errors.NotFoundException:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{obj_type.__name__} with ID {id} not found")


def delete_request_handler(id: str,
                           request: Request,
                           obj_type: type,
                           on_delete_callback: deleteRequestCallback,
                           redirect_url: str = None
                           ):
    code = None
    msg = None

    try:
        delete_result = on_delete_callback(request, id)
        logger.info(f"Delete Successful for item with id [{id}]")
    except errors.NotFoundException as e:
        code = status.HTTP_404_NOT_FOUND
        msg = f"{obj_type.__name__} with ID {id} not found. {e}"
    finally:
        if code is not None or msg is not None:
            logger.error(msg)
            raise HTTPException(status_code=code,
                                detail=msg)

        if redirect_url is not None:
            return RedirectResponse(url=redirect_url, status_code=status.HTTP_302_FOUND)
        else:
            return True
