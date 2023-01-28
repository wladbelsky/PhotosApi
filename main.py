from fastapi import FastAPI
from api import router
from static import static_router


app = FastAPI()
app.include_router(router)
app.include_router(static_router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
