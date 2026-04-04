# HTTP Methods: GET, POST, PUT, and DELETE

In web development and API design, HTTP methods (or "verbs") tell the server what kind of action the client wants to perform. The two most fundamental methods are **GET** and **POST**.

---

## 1. The GET Method

The `GET` method is used exclusively to **retrieve** or fetch data from a server. It should never be used to modify, create, or delete data on the server.

### Key Characteristics of GET

- **Read-Only:** It does not change the state of the database or server.
- **Idempotent:** Making the exact same `GET` request 1 time or 100 times will result in the same server state.
- **Data in URL:** Any data sent with a `GET` request is attached to the URL as a Query Parameter or Path Parameter.
- **Visibility & Security:** Because data is in the URL, `GET` requests are stored in browser history and server logs. **Never** send sensitive data (passwords, API keys) via a `GET` request.
- **Length Limits:** URLs have length restrictions (usually around 2048 characters), so you cannot send massive amounts of data via `GET`.
- **Caching:** `GET` responses can be cached by browsers or CDNs to improve performance.

### FastAPI Example: GET (Basic to Advanced)

```python
from fastapi import FastAPI, Query, Path

app = FastAPI()

# 1. Basic GET: Fetching a static resource
@app.get("/health")
async def health_check():
    return {"status": "System is operational"}

# 2. Intermediate GET: Using Path and Query Parameters
# URL: /datasets/101?sort_by=date&limit=50
@app.get("/datasets/{dataset_id}")
async def get_dataset(
    dataset_id: int = Path(..., title="The ID of the dataset to retrieve"),
    sort_by: str = Query("name", description="Field to sort by"),
    limit: int = Query(10, le=100) # Less than or equal to 100
):
    return {
        "dataset_id": dataset_id,
        "sorting": sort_by,
        "records_returned": limit
    }
```

---

## 2. The POST Method

The `POST` method is used to **send data** to the server to create a new resource or trigger a processing task (like running an AI model).

### Key Characteristics of POST

- **Data Mutation:** It is expected to change the server state (e.g., adding a new user to a database, uploading a file, or triggering a heavy computation).
- **Not Idempotent:** Making the exact same `POST` request 10 times might result in creating 10 duplicate records or triggering a process 10 times.
- **Data in Body:** Data is sent securely hidden inside the HTTP Request Body, not in the URL.
- **Security:** While the data is not visible in the URL, it must still be encrypted using HTTPS to be truly secure in transit.
- **No Length Limits:** You can send massive amounts of data (Megabytes or Gigabytes of JSON, images, or video files) in a `POST` request.
- **Not Cached:** `POST` requests are generally not cached because they are expected to yield different results or change state.

### FastAPI Example: POST (Basic to Advanced)

In FastAPI, you use **Pydantic** models to define the structure of the JSON body you expect to receive in a `POST` request.

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI()

# 1. Define the Request Body Schema
class InferenceRequest(BaseModel):
    text: str = Field(..., min_length=10, description="Input text for the model")
    temperature: float = Field(0.7, ge=0.0, le=1.0)
    use_cache: bool = True

# 2. Basic POST: Receiving JSON data
@app.post("/predict")
async def run_ai_model(payload: InferenceRequest):
    # FastAPI automatically reads the JSON body, validates it against InferenceRequest,
    # and maps it to the 'payload' variable.

    if payload.text == "malicious prompt":
         raise HTTPException(status_code=400, detail="Invalid input detected.")

    return {
        "received_text": payload.text,
        "used_temperature": payload.temperature,
        "prediction": "Mock AI output generated successfully."
    }

# 3. Advanced POST: Uploading Files alongside Metadata
from fastapi import File, UploadFile, Form

@app.post("/upload-dataset/")
async def upload_training_data(
    description: str = Form(...), # Form data (not JSON)
    file: UploadFile = File(...)  # Binary file upload
):
    # Reads the file contents into memory (use chunks for large files!)
    contents = await file.read()
    return {
        "filename": file.filename,
        "file_size_bytes": len(contents),
        "description": description
    }
```

---

## 3. Quick Comparison Summary

| Feature             | `GET` Request                       | `POST` Request                                 |
| :------------------ | :---------------------------------- | :--------------------------------------------- |
| **Primary Purpose** | Fetch/Retrieve data.                | Send data to create or process.                |
| **Data Location**   | URL (Path or Query string).         | HTTP Request Body.                             |
| **Data Size Limit** | Yes (Restricted by URL length).     | No (Can send large JSON/Files).                |
| **Idempotent**      | Yes (Safe to repeat).               | No (Repeating creates duplicates).             |
| **Caching**         | Can be cached.                      | Never cached.                                  |
| **Security**        | Low (Data visible in history/logs). | High (Data hidden in body, secured via HTTPS). |
| **Browser History** | Saved in history.                   | Not saved in history.                          |

---

## 4. Advanced Architect Notes: Breaking the Rules

While the definitions above are the standard RESTful principles, AI engineering sometimes requires breaking them for practical reasons.

**The "Complex Search" Exception:**
Technically, searching for data should be a `GET` request. However, if your API allows users to search using a massive, deeply nested JSON configuration (e.g., a complex Vector Database query with dozens of filters), the query string in a URL will become too long and impossible to read.

In this specific scenario, backend engineers often use a `POST` request for searching, sending the complex query parameters in the JSON body, even though the action is strictly retrieving data.

---

## HTTP Methods: PUT and DELETE

In modern RESTful APIs, while `GET` and `POST` handle fetching and creating data, `PUT` and `DELETE` are responsible for modifying and removing existing resources.

---

## 1. The PUT Method

The `PUT` method is used to **update or entirely replace** an existing resource on the server. If the resource does not exist, `PUT` can optionally be configured to create it (a process known as an "upsert").

### Key Characteristics of PUT

- **Complete Replacement:** When you send a `PUT` request, the server expects you to send the _entire_ updated object, not just the fields that changed. (If you only want to update one field, you technically should use the `PATCH` method).
- **Idempotent:** Executing the exact same `PUT` request multiple times will have the same effect as executing it once. The end state of the server remains identical.
- **Data in Body:** Like `POST`, the data to be updated is sent in the HTTP Request Body.

### FastAPI Example: PUT (Basic to Advanced)

```python
from fastapi import FastAPI, HTTPException, Path
from pydantic import BaseModel

app = FastAPI()

# Mock Database
model_configs = {
    "gpt-4": {"temperature": 0.7, "max_tokens": 1000, "active": True}
}

class ModelConfigUpdate(BaseModel):
    temperature: float
    max_tokens: int
    active: bool

# 1. Basic PUT: Replacing an existing configuration
@app.put("/models/{model_id}")
async def update_model_config(
    payload: ModelConfigUpdate,
    model_id: str = Path(..., title="The ID of the model to update")
):
    if model_id not in model_configs:
        raise HTTPException(status_code=404, detail="Model configuration not found.")

    # Completely replace the old data with the new payload
    model_configs[model_id] = payload.model_dump()

    return {"message": "Configuration updated successfully", "data": model_configs[model_id]}

# 2. Advanced PUT: The "Upsert" Pattern
# If the resource exists, update it. If it doesn't, create it.
@app.put("/datasets/{dataset_name}/metadata")
async def upsert_dataset_metadata(dataset_name: str, payload: dict):
    # Imagine checking a real database here
    is_new_creation = dataset_name not in model_configs

    # Save or overwrite the data
    model_configs[dataset_name] = payload

    # Standard practice: Return a 201 Created status if it's new,
    # or a 200 OK if it was just updated.
    if is_new_creation:
        return {"status": "created", "dataset": dataset_name}
    return {"status": "updated", "dataset": dataset_name}
```

---

## 2. The DELETE Method

The `DELETE` method does exactly what it says: it **removes** a specific resource from the server.

### Key Characteristics of DELETE

- **Destructive:** It alters the server state by removing data.
- **Idempotent:** If you delete a resource, it is gone. If you send the exact same `DELETE` request again, the state of the server doesn't change (the resource is still gone), even though the server might return a `404 Not Found` error on the second attempt.
- **No Body Required:** Usually, `DELETE` requests do not require a JSON body. The target resource is identified purely via the URL Path Parameter.

### FastAPI Example: DELETE (Basic to Advanced)

In production systems, you rarely write `DELETE` endpoints that actually erase rows from a database permanently. Instead, you use a concept called **"Soft Deletion"**.

```python
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

app = FastAPI()

# Mock Database
training_jobs = {
    101: {"status": "running", "is_deleted": False},
    102: {"status": "completed", "is_deleted": False}
}

# 1. Basic DELETE: Hard Deletion (Standard Approach)
# Notice the response_model is empty, and we return a 204 status code.
@app.delete("/jobs/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_training_job(job_id: int):
    if job_id not in training_jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    # Completely removing the record from memory/database
    del training_jobs[job_id]

    # A 204 No Content response requires NO return body.
    return

# 2. Advanced DELETE: Soft Deletion (Enterprise/Production Approach)
# We don't erase the data; we just flag it as deleted so we keep the history.
@app.delete("/secure-jobs/{job_id}")
async def soft_delete_job(job_id: int):
    if job_id not in training_jobs or training_jobs[job_id]["is_deleted"]:
        raise HTTPException(status_code=404, detail="Job not found or already deleted")

    # Update the boolean flag instead of using `del`
    training_jobs[job_id]["is_deleted"] = True

    return {
        "message": f"Job {job_id} successfully archived.",
        "note": "Data retained in database for audit logs but removed from active queries."
    }
```

---

## 3. Quick Reference Summary

| Method     | Purpose                                                            | HTTP Body?                         | Idempotent? | Typical Success Status Code                   |
| :--------- | :----------------------------------------------------------------- | :--------------------------------- | :---------- | :-------------------------------------------- |
| **PUT**    | Update or completely replace an existing resource.                 | Yes (Contains the full new object) | Yes         | `200 OK` (Updated) or `201 Created` (Upsert)  |
| **DELETE** | Remove a resource (Hard delete) or flag as inactive (Soft delete). | Generally No                       | Yes         | `200 OK` (with a message) or `204 No Content` |
