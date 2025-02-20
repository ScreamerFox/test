import uvicorn
from fastapi import FastAPI

from app.database import engine
from app.endpoints import router as endpoints_router
from app.models import Base

app = FastAPI()
app.include_router(endpoints_router)




if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=8080, workers=8)