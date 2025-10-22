# from fastapi import FastAPI
# from app.database import Base, engine
# from app.routes import router
#
# app = FastAPI()
# app.include_router(router)
#
# @app.on_event("startup")
# def on_startup():
#     Base.metadata.create_all(bind=engine)
from fastapi import FastAPI

from app.database import Base, engine
from app.routes import router

app = FastAPI()
app.include_router(router)


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)  # Создаем таблицы один раз при старте
