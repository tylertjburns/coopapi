import logging
import uuid

import requests
from typing import Dict
from fastapi import Request, HTTPException, status, Response
from coopapi.enums import RequestType

logger = logging.getLogger('coop.http')

def _response_handler(response: Response):
    pass

def _log_send(id:str, lvl: int, method: RequestType, url, label: str = None):
    _lbl_txt = f"[{label}]: " if label else ""
    logger.log(lvl, f"{_lbl_txt}{method.name} @URL: {url} [{id}]")

def _log_receive(id:str, lvl:int , method: RequestType, response: Response, url, label: str = None):
    _lbl_txt = f"[{label}]: " if label else ""
    resp_dict = {'content': response.content}
    logger.log(lvl, f"{_lbl_txt}{method.name} @URL: {url} returned {response.status_code} [{id}] in {int(response.elapsed.microseconds / 1000)} ms\n"
                     f"{resp_dict}")

def request(url: str,
            method: RequestType,
            bearer_token:str,
            loggingLvl=logging.INFO,
            label: str = None,
            request_id: str = None,
            **kwargs):
    headers = {}
    if bearer_token is not None:
        headers['Authorization'] = f"Bearer {bearer_token}"

    if request_id is None:
        request_id = str(uuid.uuid4())
    _log_send(id=request_id, lvl=loggingLvl, method=method, url=url, label=label)
    response: Response = requests.request(method=method.value, url=url, verify=True, headers=headers, **kwargs)
    _log_receive(id=request_id, lvl=loggingLvl, method=method, url=url, label=label, response=response)
    return response


def get(url: str,
        bearer_token:str = None,
        loggingLvl=logging.INFO,
        label: str = None,
        **kwargs):
    return request(url=url,
                   method=RequestType.GET,
                   bearer_token=bearer_token,
                   loggingLvl=loggingLvl,
                   label=label,
                   **kwargs)

def post(url: str,
         data: Dict,
         json: str,
         label: str = None,
         loggingLvl=logging.INFO,
         bearer_token: str = None):
    return request(url=url,
                   method=RequestType.POST,
                   bearer_token=bearer_token,
                   loggingLvl=loggingLvl,
                   label=label,
                   data=data,
                   json=json)

def put(url: str,
         data: Dict = None,
         label: str = None,
         loggingLvl=logging.INFO,
         bearer_token: str = None):
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
         bearer_token: str = None):
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
         bearer_token: str = None):
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
         bearer_token: str = None):
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
         bearer_token: str = None):
    return request(url=url,
                   method=RequestType.OPTIONS,
                   bearer_token=bearer_token,
                   loggingLvl=loggingLvl,
                   label=label,
                   data=data)

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    ret = get(url='https://w3schools.com/python/demopage.htm')