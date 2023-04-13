import logging
import uuid

import requests
from typing import Dict, Any
from fastapi import Request, HTTPException, status, Response
from coopapi.enums import RequestType
import json
import pprint
logger = logging.getLogger('coop.http')


def _response_handler(response: Response):
    pass

def _log_send(id:str, lvl: int, method: RequestType, url, label: str = None, **kwargs):
    _lbl_txt = f"[{label}]: " if label else ""
    _txt = f"{_lbl_txt}{method.name} @URL: {url} [{id}]"
    if kwargs.get('data', None) is not None:
        _txt += f"\ndata: {pprint.pformat(kwargs['data'])}"
    if kwargs.get('json', None) is not None:
        _txt += f"\njson: {pprint.pformat(kwargs['json'])}"

    logger.log(lvl, _txt)

def _log_receive(id:str, lvl:int , method: RequestType, response: Response, url, label: str = None):
    _lbl_txt = f"[{label}]: " if label else ""
    logger.log(lvl, f"{_lbl_txt}{method.name} @URL: {url} returned [{response.status_code}] [{id}] in {int(response.elapsed.microseconds / 1000)} ms\n"
                     f"{pprint.pformat(json.loads(response.content.decode(response.encoding)))}")

def request(url: str,
            method: RequestType,
            bearer_token:str=None,
            loggingLvl=logging.INFO,
            label: str = None,
            request_id: str = None,
            **kwargs) -> Response:
    headers = {}
    if bearer_token is not None:
        headers['Authorization'] = f"Bearer {bearer_token}"

    if request_id is None:
        request_id = str(uuid.uuid4())
    _log_send(id=request_id, lvl=loggingLvl, method=method, url=url, label=label, **kwargs)
    response: Response = requests.request(method=method.value, url=url, verify=True, headers=headers, **kwargs)
    _log_receive(id=request_id, lvl=loggingLvl, method=method, url=url, label=label, response=response)
    return response


def get(url: str,
        bearer_token:str = None,
        loggingLvl=logging.INFO,
        label: str = None,
        **kwargs) -> Response:
    return request(url=url,
                   method=RequestType.GET,
                   bearer_token=bearer_token,
                   loggingLvl=loggingLvl,
                   label=label,
                   **kwargs)

def post(url: str,
         data: Dict = None,
         json_serializable: Any = None,
         label: str = None,
         loggingLvl=logging.INFO,
         bearer_token: str = None) -> Response:

    return request(url=url,
                   method=RequestType.POST,
                   bearer_token=bearer_token,
                   loggingLvl=loggingLvl,
                   label=label,
                   data=data,
                   json=json_serializable)

def put(url: str,
         data: Dict = None,
         label: str = None,
         loggingLvl=logging.INFO,
         bearer_token: str = None) -> Response:
    return request(url=url,
                   method=RequestType.PUT,
                   bearer_token=bearer_token,
                   loggingLvl=loggingLvl,
                   label=label,
                   data=data)

def patch(url: str,
         data: Dict = None,
         label: str = None,
         loggingLvl=logging.INFO,
         bearer_token: str = None) -> Response:
    return request(url=url,
                   method=RequestType.PATCH,
                   bearer_token=bearer_token,
                   loggingLvl=loggingLvl,
                   label=label,
                   data=data)

def delete(url: str,
         data: Dict = None,
         label: str = None,
         loggingLvl=logging.INFO,
         bearer_token: str = None) -> Response:
    return request(url=url,
                   method=RequestType.DELETE,
                   bearer_token=bearer_token,
                   loggingLvl=loggingLvl,
                   label=label,
                   data=data)

def head(url: str,
         data: Dict = None,
         label: str = None,
         loggingLvl=logging.INFO,
         bearer_token: str = None) -> Response:
    return request(url=url,
                   method=RequestType.HEAD,
                   bearer_token=bearer_token,
                   loggingLvl=loggingLvl,
                   label=label,
                   data=data)

def options(url: str,
         data: Dict = None,
         label: str = None,
         loggingLvl=logging.INFO,
         bearer_token: str = None) -> Response:
    return request(url=url,
                   method=RequestType.OPTIONS,
                   bearer_token=bearer_token,
                   loggingLvl=loggingLvl,
                   label=label,
                   data=data)

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    ret = get(url='https://w3schools.com/python/demopage.htm')
    print(ret)