from fastapi import FastAPI

app = FastAPI()

books = [
  {
    "id": "B001",
    "title": "The Midnight Library",
    "author": "Matt Haig",
    "year": 2020,
    "category": "Fiction",
    "price": 18.99
  },
  {
    "id": "B002",
    "title": "Atomic Habits",
    "author": "James Clear",
    "year": 2018,
    "category": "Growth",
    "price": 22.50
  },
  {
    "id": "B003",
    "title": "Project Hail Mary",
    "author": "Andy Weir",
    "year": 2021,
    "category": "Science",
    "price": 25.00
  },
  {
    "id": "B004",
    "title": "The Silent Patient",
    "author": "Alex Michaelides",
    "year": 2019,
    "category": "Thriller",
    "price": 16.99
  },
  {
    "id": "B005",
    "title": "Dune",
    "author": "Frank Herbert",
    "year": 1965,
    "category": "Science",
    "price": 15.00
  }
]


@app.get("/")
async def get_home():
    return {"Message":"Welcome to the home page"}

@app.get("/books")
async def get_all_books():  
    return books 

@app.get("/books/{book_id}")
async def get_book(book_id: int):
    for book in books:
        if book['id'] == book_id :
            return book
        else :
            return {'message' : "book not found"}

@app.get("/books/")
async def get_books_by_category(category: str) :
    books_to_return = []

    for book in books:
      # print(book["category"], category.lower())
      if book['category'].lower() == category.lower():
        books_to_return.append(book)
    

    return books_to_return

# uvicorn Project01-RequestMethodLogic.books:app --reload





