from fastapi import FastAPI
from app.routes import router
from app.database import Base, engine

app = FastAPI()
app.include_router(router)

# Создать таблицы при запуске
Base.metadata.create_all(bind=engine)
