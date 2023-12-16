import os
import arel

from fastapi import FastAPI, Query
from fastapi.requests import Request
from fastapi.staticfiles import StaticFiles

from jinja2_fragments import BlockNotFoundError
from jinja2_fragments.fastapi import Jinja2Blocks
from debug_toolbar.middleware import DebugToolbarMiddleware

app = FastAPI()
app.add_middleware(DebugToolbarMiddleware)

jinja = Jinja2Blocks(directory="templates")

if _debug := os.getenv("DEBUG"):
    # Install hot reload
    hot_reload = arel.HotReload(paths=[arel.Path(".")])
    app.add_websocket_route("/hot-reload", route=hot_reload, name="hot-reload")
    app.add_event_handler("startup", hot_reload.startup)
    app.add_event_handler("shutdown", hot_reload.shutdown)
    jinja.env.globals["DEBUG"] = _debug
    jinja.env.globals["hot_reload"] = hot_reload

    jinja.env.add_extension("jinja2.ext.debug")

app.mount("/public", StaticFiles(directory="public"), name="public")

slides = [
    {
        "id": "wordpress",
        "title": "Wordpress",
        "description": "...",
        "src": "/services/wordpress?view=slider",
    },
    {
        "id": "webdesign",
        "title": "Web Design",
        "description": "...",
        "src": "/services/webdesign?view=slider",
    },
]

current_slide = 0


@app.get("/services/{service}")
async def services(request: Request, service: str, view: str | None = None):
    if request.headers.get("hx-request"):
        view = "slider"

        try:
            return jinja.TemplateResponse(
                f"services/{service}.html",
                {"request": request, "view": view},
                block_name=view,
            )
        except BlockNotFoundError:
            return 404

    return jinja.TemplateResponse(
        f"services/{service}.html", {"request": request, "is_full_page": True}
    )


@app.get("/")
async def home(request: Request):
    return jinja.TemplateResponse(
        "index.html",
        {"request": request, "slides": slides, "current_slide": current_slide},
    )
