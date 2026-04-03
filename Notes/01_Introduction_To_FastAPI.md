# Introduction to FastAPI: Understanding ASGI vs WSGI

FastAPI is a modern, fast, web framework for building APIs with Python based on standard Python type hints. As an AI Engineer, FastAPI is your go-to tool for deploying machine learning models because of its incredible performance and native support for asynchronous programming.

## 1. The Core Architecture: WSGI vs ASGI

To understand why FastAPI is so fast, you first need to understand how Python web servers communicate with web applications. If you are familiar with traditional threaded backend architectures (like Java Servlet-based Spring Boot or Python's Flask), you are used to a synchronous, blocking model.

### What is WSGI? (Synchronous / Blocking)
**WSGI** stands for **Web Server Gateway Interface**. It is the older, traditional standard for Python web frameworks (like Flask and Django). 

* **How it works:** WSGI is synchronous. When a request comes in, a worker thread handles it from start to finish. If the request involves waiting (like querying a database or running a slow AI model), that entire thread is blocked.
* **Analogy:** A cashier at a grocery store. The cashier scans items, waits for the customer to pay, and bags the groceries. During this whole process, the people in line behind them must wait.

**WSGI Example (Flask):**
```python
from flask import Flask
import time

app = Flask(__name__)

@app.route("/")
def hello_world():
    time.sleep(2)  # Blocks the entire thread for 2 seconds
    return "Hello, WSGI World!"
```

### What is ASGI? (Asynchronous / Non-Blocking)
**ASGI** stands for **Asynchronous Server Gateway Interface**. It is the modern standard designed to handle asynchronous Python code using `async` and `await`. FastAPI is built on ASGI.

* **How it works:** ASGI uses an event loop. If a request needs to wait for a database or an external API, the server pauses that specific request and frees up the thread to handle *other* incoming requests. Once the waiting is over, it resumes the original request.
* **Analogy:** A waiter in a restaurant. The waiter takes your order, hands it to the kitchen (waiting period), and instead of standing in the kitchen waiting for your food, they go take orders from other tables. 

**ASGI Example (FastAPI):**
```python
from fastapi import FastAPI
import asyncio

app = FastAPI()

@app.get("/")
async def hello_world():
    await asyncio.sleep(2)  # Pauses this request, but the server keeps serving others!
    return {"message": "Hello, ASGI World!"}
```

---

## 2. FastAPI Basics: Routing and Parameters

To run a FastAPI application, you need an ASGI server like `uvicorn`. 

**Installation:**
```bash
pip install fastapi "uvicorn[standard]"
```

**Running the app:**
```bash
uvicorn main:app --reload
```

### Path Parameters
Path parameters are embedded directly into the URL. They are typically used to identify a specific resource.

```python
from fastapi import FastAPI

app = FastAPI()

# Basic to Advanced: Notice the Python type hinting (int)
# FastAPI automatically validates that item_id is an integer.
@app.get("/models/{model_id}")
async def get_ai_model(model_id: int):
    return {"model_id": model_id, "status": "active"}
```

### Query Parameters
Query parameters appear after the `?` in the URL (e.g., `/search?query=AI&limit=10`). They are used for filtering or modifying a request.

```python
from fastapi import FastAPI

app = FastAPI()

# Default values make query parameters optional
@app.get("/search")
async def search_data(query: str, limit: int = 10):
    return {"search_query": query, "results_returned": limit}
```

---
**How to test your code:**
1. Save the code as `main.py`.
2. Run `uvicorn main:app --reload`.
3. Open your browser and go to `http://127.0.0.1:8000/docs`. FastAPI automatically generates an interactive Swagger UI documentation page where you can test your API directly!

___

# Demystifying `app = FastAPI()`: The Core Engine

## 1. The Basic View: What is `app`?
When you write `app = FastAPI()`, you are creating an **object** (an instance of the `FastAPI` class). 
Think of `app` as the central control room or the "brain" of your entire web API. 

Its primary jobs at a basic level are:
1. **Registry:** It remembers all your API endpoints (like `@app.get("/users")`).
2. **Configuration:** It holds global settings (like the title of your API, version, and documentation URLs).
3. **Coordinator:** It links your Python code to the web server (like Uvicorn).

---

## 2. The Intermediate View: Inside the `FastAPI` Object
When the `FastAPI()` class initializes, it automatically creates several internal components behind the scenes. 

### A. The Master Router (`app.router`)
FastAPI heavily relies on a lower-level framework called Starlette. Internally, `app` creates a master `APIRouter`. Every time you write `@app.get("/")`, you are actually adding that route to `app.router`. This router acts like a traffic cop, matching incoming web URLs to your specific Python functions.

### B. The Dependency Injection System
`app` initializes a registry for dependencies. When you use `Depends()`, the `app` knows how to resolve these dependencies before executing your route function (e.g., verifying a user token or getting a database connection).

### C. OpenAPI Schema Generator
By default, `app` prepares an engine to inspect all your routes and Pydantic models. It uses this inspection to automatically generate the `openapi.json` schema. This is how the `/docs` (Swagger UI) page magically appears without extra code.

---

## 3. The Advanced View: The ASGI Callable
To understand `app` deeply, you must understand how a web server (like Uvicorn) talks to your Python code. Web servers don't understand FastAPI directly; they understand the **ASGI standard** (Asynchronous Server Gateway Interface).

At its core, the `app` object is an **ASGI Callable**. In Python, an object can be executed like a function if it has a `__call__` method.

Internally, the FastAPI class implements this method:
```python
async def __call__(self, scope: dict, receive: Callable, send: Callable) -> None:
    # Internal logic to handle the web request
```

### How Uvicorn uses `app`:
When a user visits your API, Uvicorn receives the HTTP request and triggers your `app` object by "calling" it and passing three critical arguments:

1. **`scope`**: A dictionary containing all the metadata about the connection (e.g., HTTP method "GET", the path "/users", headers, client IP).
2. **`receive`**: An asynchronous function that `app` can call to read the incoming body of the request (like a JSON payload sent by the user).
3. **`send`**: An asynchronous function that `app` uses to send the final response (the headers and the data) back to the user.



---

## 4. The Request Lifecycle (Step-by-Step)
When `app` receives a request via its `__call__` method, it processes it through a strict pipeline:

1. **Middleware Stack:** The request passes through global middleware (like CORS handling or custom logging) from the outside in.
2. **Routing:** `app.router` looks at the `scope["path"]` and searches for a matching `@app.get` or `@app.post` function.
3. **Dependency Resolution:** If the route has dependencies (e.g., `db: Session = Depends(get_db)`), `app` executes those first.
4. **Data Validation:** `app` takes the incoming JSON (using `receive`), passes it to Pydantic to ensure it matches your models, and throws a `422 Unprocessable Entity` error automatically if it doesn't.
5. **Execution:** Your actual Python function runs.
6. **Serialization:** `app` takes the Python dictionary or Pydantic model you returned, and converts it back to standard JSON.
7. **Response:** `app` uses the `send` function to shoot the HTTP response back through Uvicorn to the user.

---

## 5. Summary Code Conceptualization
Here is a conceptual representation of what happens internally:

```python
# 1. You create the instance (The ASGI Callable is born)
app = FastAPI() 

# 2. You register a route (Added to app.router's internal list)
@app.get("/status") 
async def system_status():
    return {"status": "ok"}

# 3. Uvicorn running in the background essentially does this for EVERY request:
# (This is highly simplified pseudocode to show the internal ASGI interaction)

# incoming_scope = {"type": "http", "method": "GET", "path": "/status", ...}
# await app(incoming_scope, receive_data_stream, send_data_stream)
```