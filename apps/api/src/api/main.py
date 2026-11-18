from fastapi import FastAPI

from api.modules.auth.router import router as auth_router
from api.modules.me.router import router as me_router
from api.modules.memberships.router import router as memberships_router

app = FastAPI(title="Insights Platform API", version="0.1.0")


@app.get("/health", tags=["health"])
def health() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(auth_router)
app.include_router(me_router)
app.include_router(memberships_router)
