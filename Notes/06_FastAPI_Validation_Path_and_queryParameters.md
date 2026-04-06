# FastAPI Validation: Path and Query Parameters

While standard Pydantic models are perfect for validating the JSON body of a `POST` request, you cannot use them directly to validate the URL. For data that comes through the URL, FastAPI provides two special functions: `Path` and `Query`.

Under the hood, these functions actually use Pydantic to do the heavy lifting, meaning you get the exact same powerful validation and automatic Swagger UI documentation.

---

## 1. Validating Query Parameters (`Query`)

Query parameters appear after the `?` in the URL (e.g., `/search?query=AI&limit=10`). 

### A. Basic String Validation
You can enforce length and patterns (Regex) to ensure users don't send garbage data or attempt basic injection attacks.

```python
from fastapi import FastAPI, Query

app = FastAPI()

@app.get("/search")
async def search_datasets(
    # Optional parameter (defaults to None)
    # Must be between 3 and 50 characters
    # Must only contain letters, numbers, and spaces
    q: str | None = Query(
        default=None,
        min_length=3,
        max_length=50,
        pattern="^[a-zA-Z0-9 ]+$"
    )
):
    return {"search_term": q}
```

### B. Required vs. Optional Queries
In modern Python/FastAPI, if you want a query parameter to be strictly required, you do not give it a default value. If you need to use the `Query()` function to add validation to a required parameter, you use `...` (the Python Ellipsis) as the default value.

```python
from fastapi import FastAPI, Query

app = FastAPI()

@app.get("/models")
async def list_models(
    # This query parameter is strictly REQUIRED. 
    # If the user omits ?framework=..., FastAPI throws a 422 Error.
    framework: str = Query(..., min_length=2)
):
    return {"filtering_by": framework}
```

### C. Lists in Query Parameters
Sometimes you want to filter by multiple tags at once. 
URL Example: `/datasets?tags=nlp&tags=vision&tags=audio`

```python
from fastapi import FastAPI, Query

app = FastAPI()

@app.get("/datasets")
async def get_datasets(
    # Accepts multiple values into a Python list
    tags: list[str] = Query(
        default=["general"], # Default if none provided
        description="Filter datasets by multiple tags"
    )
):
    return {"applied_tags": tags}
```

---

## 2. Validating Path Parameters (`Path`)

Path parameters are embedded directly inside the URL (e.g., `/users/123`). 
*Note: Because they are part of the URL route itself, Path parameters are **always required**. You cannot make them optional.*

### A. Numerical Boundaries
This is highly useful for IDs or requesting a specific number of items.

```python
from fastapi import FastAPI, Path

app = FastAPI()

@app.get("/jobs/{job_id}")
async def get_training_job(
    # ge = Greater than or equal to 1
    # le = Less than or equal to 1000
    job_id: int = Path(..., title="The ID of the training job", ge=1, le=1000)
):
    return {"job_id": job_id}
```

### B. String Validation in Paths
You can also apply Regex and length limits to URLs.

```python
from fastapi import FastAPI, Path

app = FastAPI()

@app.get("/projects/{project_code}")
async def get_project(
    # Enforce exactly 5 alphanumeric characters (e.g., /projects/AI101)
    project_code: str = Path(..., min_length=5, max_length=5, pattern="^[A-Z0-9]+$")
):
    return {"project_code": project_code}
```

---

## 3. Swagger UI Integration (Metadata)

Just like the Pydantic `Field` function, `Path` and `Query` allow you to inject rich metadata directly into your Swagger UI `/docs` page.

```python
from fastapi import FastAPI, Path, Query

app = FastAPI()

@app.get("/api/v1/generate/{engine}")
async def generate_text(
    # Path Metadata
    engine: str = Path(
        ..., 
        title="AI Engine Name",
        description="The backend LLM engine to use (e.g., gpt-4, claude).",
        examples=["gpt-4"]
    ),
    
    # Query Metadata with an Alias
    # The URL will look like: ?x-custom-temp=0.7
    temperature: float = Query(
        default=0.7,
        alias="x-custom-temp",
        title="Generation Temperature",
        description="Controls creativity. Higher is more random.",
        ge=0.0,
        le=2.0,
        deprecated=False
    )
):
    return {"engine": engine, "temp": temperature}
```

---

## 4. Advanced: Using Pydantic Models for Query Parameters

If your `GET` request has a massive amount of query parameters (e.g., a complex search filter for a vector database), passing 10 different `Query()` arguments into your function gets very messy.

Instead, you can define a Pydantic model to represent your query parameters, and use FastAPI's `Depends()` to tell the framework to parse the URL into that model.

```python
from fastapi import FastAPI, Depends
from pydantic import BaseModel, Field

app = FastAPI()

# 1. Define a Pydantic model for the URL queries
class DataSearchFilter(BaseModel):
    query_text: str = Field(..., min_length=3)
    limit: int = Field(10, ge=1, le=100)
    include_archived: bool = False
    author_id: int | None = None

# 2. Inject it using Depends()
@app.get("/search-advanced")
async def advanced_search(filters: DataSearchFilter = Depends()):
    # FastAPI automatically extracts ?query_text=xyz&limit=50&include_archived=true
    # validates it using Pydantic, and gives you a clean object!
    
    return {
        "search_term": filters.query_text,
        "max_results": filters.limit,
        "include_archived": filters.include_archived
    }
```