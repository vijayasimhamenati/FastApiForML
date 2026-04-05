from fastapi import FastAPI, Body
from pydantic import BaseModel

app = FastAPI()

class Book():
  book_id : int
  title : str
  author : str
  description : str 
  rating : int 
  price : float

  def __init__(self,book_id : int, title: str, author:str, description:str, rating:int, price:float ):
    self.book_id = book_id
    self.title = title
    self.author = author
    self.description = description
    self.rating = rating
    self.price = price

class BookRequest(BaseModel):
  book_id : int
  title : str
  author : str
  description : str 
  rating : int 
  price : float


  
books = [Book(1,"title 1","author 1","description 1", 5,99.99 ),
         Book(2,"title 2","author 2","description 2", 4.5,85.95 ),
         Book(3,"title 3","author 3","description 3", 4,56 ),
         Book(4,"title 4","author 2","description 4", 5,45.6 ),
         Book(1,"title 5","author 1","description 5", 2,120 )]

@app.get("/")
async def health_check():
  return {"message": "Server is working"}

@app.get("/books")
async def read_all_books():
  return books
# the framework automatically handles serialization, validation, and documentation based on how you define the endpoints

# @app.post("/books/create_book")
# async def create_book(book = Body()):
#   books.append(Book(**book)) # ** Unpacking the dictionary
#   return {"message": "inserted the book"}
# # create method without validation

@app.post("/books/create_book")
async def create_book(book : BookRequest):
  print(type(book))
  books.append(Book(**book.model_dump())) # ** Unpacking the dictionary
  return {"message": "inserted the book"}
  

# uvicorn Project02-Validations.books2:app
