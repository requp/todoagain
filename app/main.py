import uvicorn
from fastapi import FastAPI

from app.auth import user_router, auth_router
from app.backend.config import ROOT_API


app = FastAPI()
app_v1 = FastAPI(
    redirect_slashes=False
)


app.mount("/v1", app_v1)

@app.get(ROOT_API + "/")
async def welcome() -> dict:
    return {"message": "My todo app"}


app.include_router(user_router.router)
app.include_router(auth_router.router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8888)