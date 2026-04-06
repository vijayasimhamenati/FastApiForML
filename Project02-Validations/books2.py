from fastapi import FastAPI, Body
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional

app = FastAPI()

class Book():
  book_id : int
  title : str
  author : str
  description : str 
  rating : int 
  price : float
  publish_year : int

  def __init__(self,book_id : int, title: str, author:str, description:str, rating:int, price:float, publish_year: int ):
    self.book_id = book_id
    self.title = title
    self.author = author
    self.description = description
    self.rating = rating
    self.price = price
    self.publish_year = publish_year

class BookRequest(BaseModel):
  book_id : Optional[int] = None
  title : str = Field(min_length=3, max_length= 25, description="title can be max of 25 characters")
  author : str = Field(min_length= 2, max_length= 25, description="author can be of max 25 characters")
  description : str = Field(min_length=10, max_length=100, description="description can be of maximun 100 characters")
  rating : int = Field(le=5, gt=0, description="rating can be between 1 and 5")
  price : float = Field( gt=0, description="price should be gt 0")
  publish_year : int = Field(ge= 2000, le= 2026, description="books publication shoyld be between 2000 and 2026")

  # Injects a custom JSON example directly into the Swagger UI request body
  model_config = ConfigDict(
    json_schema_extra= {
      "example" : {
        "title" : "title sample",
        "author" : "author sample",
        "description" : "This is a example description",
        "rating" : 5,
        "price" : 100,
        "publish_year" : 2026
      }
    }
  )


  
books = [Book(1,"title 1","author 1","description 1", 5,99.99, 2002 ),
         Book(2,"title 2","author 2","description 2", 4.5,85.95, 2005 ),
         Book(3,"title 3","author 3","description 3", 4,56, 2024 ),
         Book(4,"title 4","author 2","description 4", 5,45.6, 2024 ),
         Book(5,"title 5","author 1","description 5", 2,120, 2023 )]

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

# searches book by id and returns the book
@app.get("/books/{book_id}")
async def read_book_by_id(book_id : int):
  for book in books :
    if book.book_id == book_id :
      return book
  else : 
    return {"message": "Book not found"}
  

@app.get("/books/")
async def get_books_by_rating(rating : int):
  books_to_return= []
  for book in books:
    if book.rating >= rating :
      books_to_return.append(book)

  return books_to_return

@app.get("/books/year/")
async def get_books_by_publication_year(publication_year: int):
  books_to_return = []
  for book in books:
    if book.publish_year == publication_year:
      books_to_return.append(book)
  return books_to_return

@app.post("/books/create_book")
async def create_book(book : BookRequest):
  # print(type(book))
  books.append(
    create_id(
      Book(**book.model_dump()))) # ** Unpacking the dictionary
  return {"message": "inserted the book"}

@app.put("/books/update_book/{book_id}")
async def update_book_by_id(book_id : int, book :BookRequest):
  for i in range(len(books)):
    if books[i].book_id == book_id :
      book.book_id = book_id
      books[i] = book
      return {"message" : "Updated"}
  else :
    return {"message": "No such book found"}

@app.delete("/books/delete_book/{book_id}")
async def delete_book_by_id(book_id: int):
  for i in range(len(books)):
    if books[i].book_id == book_id :     
      books.pop(i)
      return {"message" : "deleted"}
  else :
    return {"message": "No such book found"}


def create_id(book):
  book_id = 1 if len(books) == 0 else len(books)+1
  print(book_id)
  book.book_id = book_id
  return book


  

# uvicorn Project02-Validations.books2:app --reload
