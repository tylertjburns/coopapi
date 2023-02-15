from fastapi import Body, Request, status
from coopapi import http_request_handlers as hrh
from typing import Any, Dict, List, Callable, Tuple
from fastapi import APIRouter
from pydantic.dataclasses import dataclass as pydataclass, Field
from dataclasses import dataclass, field
import json
from urllib.parse import parse_qs
import logging

logger = logging.getLogger('APIHandler')

def post_route(create_callback: hrh.postRequestCallback,
               schema: type):
    def create(request: Request, item: schema = Body(...)) -> schema:
        ret = hrh.post_request_handler(request=request,
                                       item=item,
                                       on_post_callback=create_callback
                                       )

        return ret
    return create

def put_route(update_callback: hrh.putRequestCallback,
              schema: type):
    def update(request: Request, id: str, update_values: Dict = Body(...)) -> schema:
        return hrh.put_request_handler(request=request,
                                       id=id,
                                       obj_type=schema,
                                       update_values=update_values,
                                       on_put_callback=update_callback)
    return update

def delete_route(delete_callback: hrh.deleteRequestCallback,
                 schema: type,
                 redirect_url: str = None):
    def delete(request: Request, id: str):
        return hrh.delete_request_handler(id=id,
                                          request=request,
                                          obj_type=schema,
                                          on_delete_callback=delete_callback,
                                          redirect_url=redirect_url)
    return delete

def getone_route(find_callback: hrh.getOneRequestCallback,
                 schema: type):
    def find(request: Request, id: str) -> schema:
        return hrh.getone_request_handler(id=id,
                                          request=request,
                                          obj_type=schema,
                                          on_getone_callback=find_callback)
    return find

def getmany_route(list_callback: hrh.getManyRequestCallback,
                  schema: type):
    def list(request: Request, query: str = None, limit: int = 100) -> List[schema]:
        if query is not None:
            query = json.loads(query)
        ret = hrh.getmany_request_handler(request,
                                          on_getmany_callback=list_callback,
                                          query=query,
                                          limit=limit)
        return ret
    return list


dirtyCleaner = Callable[[Dict], Dict]

def dirty_post_route(create_callback: hrh.postRequestCallback,
                     schema: type,
                     cleaner: dirtyCleaner):
    def dirty_post_route(request: Request, dirty_str: str = Body(...)) -> schema:
        dirty_data = parse_qs(dirty_str)
        clean_data = cleaner(dirty_data)
        logger.info(f"Received Data: {dirty_str}\n"
                    f"Cleaned Data: {clean_data}")

        obj = schema(**clean_data)
        ret = hrh.post_request_handler(request=request,
                                       item=obj,
                                       on_post_callback=create_callback
                                       )

        return ret
    return dirty_post_route

# class Config:
#     arbitrary_types_allowed = True

@dataclass
class ApiShell:
    target_schema: type
    base_route: str
    on_post_callback: hrh.postRequestCallback = field(default=None)
    on_put_callback: hrh.putRequestCallback = field(default=None)
    on_delete_callback: hrh.deleteRequestCallback = field(default=None)
    on_getone_callback: hrh.getOneRequestCallback = field(default=None)
    on_getmany_callback: hrh.getManyRequestCallback = field(default=None)
    dirty_create: dirtyCleaner = field(default=None)
    router: APIRouter = field(default_factory=APIRouter)


    def __post_init__(self):
        self.register_routes()
        print(f"{self.base_route} routes registered")

    # def __post_init_post_parse__(self):
    #     self.register_routes()
    #     print(f"{self.base_route} routes registered")

    def register_routes(self):
        '''
        Basic CRUD api_routers routes
        '''
        # create route
        if self.on_post_callback is not None:
            self.router.add_api_route(
                f"{self.base_route}/api/",
                post_route(self.on_post_callback, schema=self.target_schema),
                methods=['POST'],
                response_description=f"POST a new {self.target_schema.__name__}",
                response_model=self.target_schema,
                status_code=status.HTTP_201_CREATED)

        # update route
        if self.on_put_callback is not None:
            self.router.add_api_route(
                f"{self.base_route}/api/{{id}}",
                put_route(update_callback=self.on_put_callback, schema=self.target_schema),
                methods=['PUT'],
                response_description=f"PUT a {self.target_schema.__name__}",
                response_model=self.target_schema,
                status_code=status.HTTP_202_ACCEPTED
            )

        # delete route
        if self.on_delete_callback is not None:
            self.router.add_api_route(
                f"{self.base_route}/api/{{id}}",
                delete_route(delete_callback=self.on_delete_callback, schema=self.target_schema),
                methods=['DELETE'],
                response_description=f"DELETE a {self.target_schema.__name__}",
                response_model=bool,
                status_code=status.HTTP_200_OK
            )

        # find route
        if self.on_getone_callback is not None:
            self.router.add_api_route(
                f"{self.base_route}/api/{{id}}",
                getone_route(find_callback=self.on_getone_callback, schema=self.target_schema),
                methods=['GET'],
                response_description=f"GET a single {self.target_schema.__name__} by id",
                response_model=self.target_schema,
                status_code=status.HTTP_200_OK)

        # list route
        if self.on_getmany_callback is not None:
            self.router.add_api_route(
                f"{self.base_route}/api/",
                getmany_route(list_callback=self.on_getmany_callback, schema=self.target_schema),
                methods=['GET'],
                response_description=f"GET all {self.target_schema.__name__}s",
                response_model=List[self.target_schema],
                status_code=status.HTTP_200_OK
            )


        '''
        routes specific to being accessed via HTML elements. Since all hrefs assume a requirement for 'GET' requests,
        they must be structured differently. Rather than using the /api_routers/ routes, instead, include the operation 
        (eg, 'delete') in the url, and send it as a 'GET' route. These should include redirect_urls back to the base
        route.
        '''

        if self.on_delete_callback is not None:
            self.router.add_api_route(
                f"{self.base_route}/delete/{{id}}",
                delete_route(delete_callback=self.on_delete_callback, schema=self.target_schema, redirect_url=f"{self.base_route}"),
                methods=['GET'],
                response_description=f"Delete a {self.target_schema.__name__}",
                response_model=bool,
                status_code=status.HTTP_200_OK
            )

        '''
        Dirty route (used for taking in data in a format we know wont work directly, but can be manipulated to use
        the endpoints
        '''
        if self.dirty_create is not None:
            if self.on_post_callback is None:
                raise NotImplementedError(f"Cannot supply a dirty create without an on_create_callback")

            self.router.add_api_route(
                f"{self.base_route}/dirty/",
                dirty_post_route(create_callback=self.on_post_callback, schema=self.target_schema, cleaner=self.dirty_create),
                methods=['POST'],
                response_description=f"Create a {self.target_schema.__name__}",
                response_model=self.target_schema,
                status_code=status.HTTP_200_OK
            )




if __name__ == "__main__":
    from models.ledger import LedgerSchema
    from api.ledger_router import LedgerMongoCollectionHandler, LedgerFacade
    from mongo import mongo_utils as utils
    import config

    ledger_facade_handler = utils.DocumentFacadeHandler(
        facade_type=LedgerFacade,
        obj_type=LedgerSchema)

    ledger_collection_handler = LedgerMongoCollectionHandler(
        db_name='testdb',
        collection_name='ledger',
        uri=utils.connection_string_uri(user=config.user(),
                                        pw=config.pw(),
                                        uri_template=config.uri_template()),
        facade_handler=ledger_facade_handler
    )

    cb: hrh.postRequestCallback = lambda req, T: next(iter(ledger_collection_handler.add_items([T])))
    shell = ApiShell(schema=LedgerSchema, on_create_callback=cb)