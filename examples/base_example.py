from examples.dummySchema import DummySchema
from coopapi import createRequestCallback, ApiShell, deleteRequestCallback
import uvicorn
from fastapi import FastAPI

# create the callbacks for what should be done when the various endpoints are called. This is likely a
# db interaction or a forwarding request.
create_callback: createRequestCallback = lambda r, t: t
delete_callback: deleteRequestCallback = lambda r, t: True

# setup the api itself, use a base FastAPI object and then an api_shell which has its router included in the
# base api
app = FastAPI()
api_shell = ApiShell(target_schema=DummySchema,
                     base_route='/dummy',
                     on_create_callback=create_callback,
                     on_delete_callback=delete_callback)
app.include_router(api_shell.router, tags=["dummy_shell"])


# serve the app
uvicorn.run(app, port=1219)