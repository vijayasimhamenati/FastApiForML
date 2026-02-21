from fastapi import FastAPI

app = FastAPI()

books = [
  {
    "id": 1,
    "title": "To Kill a Mockingbird",
    "author": "Harper Lee",
    "year": 1960
  },
  {
    "id": 2,
    "title": "1984",
    "author": "George Orwell",
    "year": 1949
  },
  {
    "id": 3,
    "title": "The Great Gatsby",
    "author": "F. Scott Fitzgerald",
    "year": 1925
  },
  {
    "id": 4,
    "title": "The Catcher in the Rye",
    "author": "J.D. Salinger",
    "year": 1951
  },
  {
    "id": 5,
    "title": "Pride and Prejudice",
    "author": "Jane Austen",
    "year": 1813
  }
]


@app.get("/books")
async def get_all_books():
    return books

@app.get("/")
async def get_home():
    return {"Message":"Welcome to the home page"}

