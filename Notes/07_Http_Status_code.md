# FastAPI: Mastering HTTP Status Codes

When building professional APIs, returning the correct HTTP status code is just as important as returning the right data. It tells the client application exactly what happened—whether the AI model successfully generated a response, if the input data was invalid, or if the server crashed.

In FastAPI, you should avoid typing raw numbers (like `200` or `404`). Instead, use the built-in `status` module, which provides auto-completing, readable variables (like `status.HTTP_404_NOT_FOUND`).

```python
from fastapi import FastAPI, status, HTTPException

app = FastAPI()
```

---

## 1. The 2xx Series: Success

The `2xx` series means the client's request was successfully received, understood, and accepted. You usually define these as the default success code directly in your route decorator.

* **200 OK (`status.HTTP_200_OK`)**: The standard response for a successful request (GET, PUT, PATCH). FastAPI uses this by default if you don't specify anything.
* **201 Created (`status.HTTP_201_CREATED`)**: Used exclusively when a completely new resource was created on the server (usually a POST request).
* **204 No Content (`status.HTTP_204_NO_CONTENT`)**: The server successfully processed the request, but is not returning any data. Highly common for successful `DELETE` requests.

**Code Example:**
```python
from fastapi import FastAPI, status
from pydantic import BaseModel

app = FastAPI()

class ModelConfig(BaseModel):
    name: str

# Example 1: 201 Created
@app.post("/models", status_code=status.HTTP_201_CREATED)
async def create_custom_model(config: ModelConfig):
    # Logic to save the model configuration
    return {"message": "Model created", "model_name": config.name}

# Example 2: 204 No Content (Notice there is no return statement)
@app.delete("/models/{model_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_model(model_id: str):
    # Logic to delete the model from the database
    pass 
```

---

## 2. The 3xx Series: Redirection

The `3xx` series tells the client that they need to go to a different URL to get the resource they are looking for. 

* **307 Temporary Redirect (`status.HTTP_307_TEMPORARY_REDIRECT`)**: The resource is temporarily at a different URL.
* **308 Permanent Redirect (`status.HTTP_308_PERMANENT_REDIRECT`)**: The resource has moved permanently. Browsers will cache this and automatically go to the new URL next time.

**Code Example:**
```python
from fastapi import FastAPI
from fastapi.responses import RedirectResponse

app = FastAPI()

@app.get("/legacy-inference-endpoint")
async def redirect_to_new_endpoint():
    # If users hit the old API, redirect them to the v2 API automatically
    return RedirectResponse(url="/v2/inference", status_code=status.HTTP_308_PERMANENT_REDIRECT)
```

---

## 3. The 4xx Series: Client Errors

The `4xx` series means the **client messed up**. They sent bad data, tried to access something they shouldn't, or looked for something that doesn't exist. In FastAPI, you handle these by explicitly raising an `HTTPException`.

* **400 Bad Request (`status.HTTP_400_BAD_REQUEST`)**: The request was malformed or violates a specific business rule (e.g., trying to set a temperature of 5.0 when the max is 2.0).
* **401 Unauthorized (`status.HTTP_401_UNAUTHORIZED`)**: The user has not logged in or provided a valid API key.
* **403 Forbidden (`status.HTTP_403_FORBIDDEN`)**: The user *is* logged in, but they do not have the required permissions (e.g., a standard user trying to delete a system database).
* **404 Not Found (`status.HTTP_404_NOT_FOUND`)**: The requested URL or specific resource (like a specific user ID) does not exist.
* **422 Unprocessable Entity (`status.HTTP_422_UNPROCESSABLE_ENTITY`)**: This is **FastAPI's signature error**. If a user sends a string when Pydantic expected an integer, FastAPI automatically returns a 422 before your code even runs.

**Code Example:**
```python
from fastapi import FastAPI, HTTPException, status

app = FastAPI()

mock_database = {"101": "llama-3"}

@app.get("/models/{model_id}")
async def get_model_info(model_id: str, api_key: str | None = None):
    # 401 Error: No API Key
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="API Key is required to access models."
        )
        
    # 403 Error: Has key, but wrong tier
    if api_key == "free_tier_key" and model_id == "101":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Your subscription tier does not allow access to premium models."
        )

    # 404 Error: Model doesn't exist
    if model_id not in mock_database:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Model with ID {model_id} was not found."
        )
        
    return {"model": mock_database[model_id]}
```

---

## 4. The 5xx Series: Server Errors

The `5xx` series means the **backend messed up**. The client sent a perfectly valid request, but your Python code crashed, the database went offline, or a third-party API failed.

* **500 Internal Server Error (`status.HTTP_500_INTERNAL_SERVER_ERROR`)**: The generic "something broke" error. If your Python code throws an unhandled exception (like a `KeyError` or `ZeroDivisionError`), FastAPI automatically returns a 500.
* **502 Bad Gateway (`status.HTTP_502_BAD_GATEWAY`)**: Your API is sitting behind a load balancer or acting as a proxy, and the downstream server (like an external OpenAI server) returned an invalid response.
* **503 Service Unavailable (`status.HTTP_503_SERVICE_UNAVAILABLE`)**: The server is overloaded or down for maintenance. 

**Code Example:**
```python
from fastapi import FastAPI, HTTPException, status

app = FastAPI()

@app.post("/heavy-computation")
async def run_computation():
    try:
        # Imagine this calls an external GPU cluster that is currently offline
        result = 10 / 0 
    except ZeroDivisionError:
        # You can manually catch backend errors and return a clean 500 response
        # instead of letting the raw Python traceback leak to the client.
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="The computation engine encountered a critical error. Our team has been notified."
        )
    return {"result": result}
```