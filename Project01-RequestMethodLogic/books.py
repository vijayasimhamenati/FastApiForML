from fastapi import FastAPI

app = FastAPI()

@app.get("/books")
async def get_books():
    return {"message":"All books"}

@app.get("/")
async def get_home():
    return {"Message":"Welcome to the home page"}

