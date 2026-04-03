# FastAPI: Path Parameters and Query Parameters

In building APIs, you need ways for clients (users or front-end apps) to send small pieces of data to your backend. In FastAPI, the two most common ways to send data via the URL are **Path Parameters** and **Query Parameters**.

---

## 1. Path Parameters

Path parameters are variables embedded directly inside the URL path. They are generally used to **identify a specific resource** (like a specific user, item, or database record).

### Basic Path Parameters
You define path parameters by wrapping them in curly braces `{}` inside the route decorator, and then pass them as arguments to your function.

```python
from fastapi import FastAPI

app = FastAPI()

# URL Example: http://127.0.0.1:8000/users/42
@app.get("/users/{user_id}")
async def get_user(user_id: int):
    # FastAPI automatically converts '42' from a string to an integer!
    # If the user sends /users/abc, FastAPI returns an automatic Error 422.
    return {"user_id": user_id, "status": "active"}
```

### Advanced: Order Matters
Because URLs are evaluated from top to bottom, fixed paths must be declared *before* dynamic path parameters.

```python
from fastapi import FastAPI

app = FastAPI()

# CORRECT: Fixed path comes first
@app.get("/users/me")
async def get_current_user():
    return {"user_id": "current_logged_in_user"}

# Dynamic path comes second
@app.get("/users/{user_id}")
async def get_user(user_id: str):
    return {"user_id": user_id}
```
*If you reversed the order, the router would think "me" is just another `user_id`.*

### Advanced: Predefined Values (Enums)
If you want a path parameter to *only* accept specific, predefined values (like limiting an AI model type), use Python's `Enum`.

```python
from enum import Enum
from fastapi import FastAPI

app = FastAPI()

class ModelName(str, Enum):
    gpt4 = "gpt-4"
    claude = "claude-3"
    llama = "llama-3"

# URL Example: /models/llama-3
@app.get("/models/{model_name}")
async def get_model(model_name: ModelName):
    # model_name is restricted to the 3 options above.
    if model_name == ModelName.gpt4:
        return {"model": model_name, "message": "Using OpenAI"}
    return {"model": model_name, "message": "Using Open Source"}
```

### Advanced: Stringent Validation with `Path()`
Sometimes just checking the data type (like `int`) isn't enough. You can use FastAPI's `Path` function to add strict validation rules.

```python
from fastapi import FastAPI, Path

app = FastAPI()

@app.get("/items/{item_id}")
async def read_item(
    item_id: int = Path(..., title="The ID of the item", ge=1, le=1000)
):
    # `...` means it is required.
    # ge=1 means Greater than or Equal to 1
    # le=1000 means Less than or Equal to 1000
    return {"item_id": item_id}
```

---

## 2. Query Parameters

Query parameters appear at the end of the URL, after a question mark `?`, and are separated by ampersands `&`. They are generally used to **filter, sort, or paginate** a list of resources.

*Example URL:* `http://127.0.0.1:8000/items/?skip=0&limit=10`

### Basic Query Parameters
When you declare other function arguments that are **not** part of the path `{}` variables, FastAPI automatically interprets them as query parameters.

```python
from fastapi import FastAPI

app = FastAPI()

fake_items_db = [{"item_name": "Foo"}, {"item_name": "Bar"}, {"item_name": "Baz"}]

# URL Example: /items/?skip=0&limit=2
@app.get("/items/")
async def read_items(skip: int = 0, limit: int = 10):
    # Because skip and limit have default values, they are optional.
    return fake_items_db[skip : skip + limit]
```

### Optional Query Parameters
If a query parameter is not required, you should set its default value to `None`. In modern Python (3.10+), you use `| None` to denote this.

```python
from fastapi import FastAPI

app = FastAPI()

# URL Example: /search?q=machine+learning
@app.get("/search")
async def search(q: str | None = None):
    if q:
        return {"search_query": q, "results": ["result 1", "result 2"]}
    return {"search_query": "No query provided"}
```

### Advanced: Stringent Validation with `Query()`
Just like `Path()`, you can use `Query()` to enforce rules, add metadata for the Swagger documentation, or accept lists of values.

```python
from fastapi import FastAPI, Query

app = FastAPI()

@app.get("/products/")
async def get_products(
    q: str | None = Query(
        default=None, 
        min_length=3, 
        max_length=50, 
        pattern="^[a-zA-Z0-9 ]*$", # Only alphanumeric and spaces
        description="Search query for products"
    )
):
    return {"search_term": q}
```

### Advanced: Multiple Query Parameters / Lists
You can accept multiple values for the same query parameter.
*Example URL:* `/items/?tags=ai&tags=python&tags=fastapi`

```python
from fastapi import FastAPI, Query

app = FastAPI()

@app.get("/items/")
async def read_items(tags: list[str] | None = Query(default=None)):
    return {"tags_provided": tags} 
    # Output: {"tags_provided": ["ai", "python", "fastapi"]}
```

---

## 3. Path vs. Query: When to use which?

| Feature | Path Parameters (`{param}`) | Query Parameters (`?param=value`) |
| :--- | :--- | :--- |
| **Purpose** | To identify a specific resource. | To filter, sort, or modify the response. |
| **Placement** | Embedded in the URL path (e.g., `/users/123`). | Appended to the URL (e.g., `/users?role=admin`). |
| **Required?** | **Always required** (unless you use complex routing tricks). | Usually **optional** (but can be made required). |
| **Analogy** | The house number on a street. | Instructions on how to sort the mail delivered to that house. |

---

## 4. Putting It All Together

In real-world AI applications, you will frequently combine both in a single endpoint.

```python
from fastapi import FastAPI, Path, Query

app = FastAPI()

# Example: Get logs for a specific AI model (Path) and filter them by date/severity (Query)
# URL: /models/gpt-4/logs?severity=error&limit=5

@app.get("/models/{model_name}/logs")
async def get_model_logs(
    # Path Parameter
    model_name: str = Path(..., title="The name of the AI model"),
    
    # Query Parameters
    severity: str | None = Query(default="info", description="Log level: info, warning, error"),
    limit: int = Query(default=10, le=100)
):
    return {
        "target_model": model_name,
        "filters_applied": {"severity": severity, "limit": limit},
        "logs": ["log1", "log2"] # Mocked data
    }
```