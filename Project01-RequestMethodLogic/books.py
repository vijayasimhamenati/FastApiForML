from fastapi import FastAPI, Body

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

@app.get("/health-check")
async def health_check():
    return {"Health": "Success",
        "Message" : "API server is working"}

@app.get("/books")
async def get_all_books():  
    return books 

@app.get("/books/{book_id}")
async def get_book(book_id: str):
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

@app.get("/book/")
async def get_books_by_author(author_name: str):
    books_to_return =[]
    for book in books:        
        if book.get("author").lower() == author_name.lower():
            books_to_return.append(book)

    if len(books_to_return)!=0:
        return books_to_return
    else:
        return{"message" : "No books registered with given author"}


@app.post("/books/create_book")
async def create_book(new_book=Body()):
    books.append(new_book)
    return {"message" : "book created successfully",
            "book" : new_book}

@app.put("/books/update_book/{book_id}")
async def update_book(book_id: str, updated_book=Body()):
    # books[book_id] = updated_book
    book_index = None
    for book in books:
        if book['id'] == book_id :
            book_index = books.index(book)
            break
    if book_index is not None:
        books[book_index] = updated_book

    return {"message" : "book updated successfully"},

@app.delete("/books/delete_book/{book_title}")
async def delete_book(book_title : str):
    book_to_delete = None
    for i in range(len(books)):
        
        books[i].get("title").lower() == book_title.lower()
        book_to_delete = i
        break
    books.pop(book_to_delete)

    return {"message" : "Book deleted successfully"}

# uvicorn Project01-RequestMethodLogic.books:app --reload





