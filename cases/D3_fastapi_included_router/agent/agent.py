"""Turns a FastAPI app into a tool list for an agent: one tool per (method, path)."""
from fastapi import APIRouter, FastAPI

items = APIRouter(prefix="/items")
users = APIRouter(prefix="/users")


@items.get("/{item_id}")
def get_item(item_id: int):
    return {"id": item_id}


@items.post("/")
def create_item():
    return {}


@users.get("/me")
def me():
    return {}


app = FastAPI()
app.include_router(items)
app.include_router(users)


def tool_table() -> list[tuple[str, str]]:
    out = []
    for route in app.routes:
        if route.path.startswith(("/docs", "/openapi", "/redoc")):
            continue
        for method in sorted(route.methods or []):
            if method != "HEAD":
                out.append((method, route.path))
    return sorted(out)
