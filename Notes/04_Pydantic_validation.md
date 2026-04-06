# Pydantic in FastAPI - Part 1: Basic Types and Field Validation

In FastAPI, Pydantic is the engine that handles data parsing and validation. When an external client sends JSON data to your API, Pydantic ensures the data matches your exact requirements before your Python code even runs.

## 1. Standard Python Type Hints

At its most basic level, Pydantic uses standard Python type hints. If a user sends the wrong data type (e.g., sending a string like "high" instead of a float for temperature), Pydantic automatically intercepts it and returns a `422 Unprocessable Entity` error with a clear message.

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

# The blueprint for incoming JSON data
class AIModelRequest(BaseModel):
    prompt: str
    temperature: float
    max_tokens: int
    stream_response: bool

@app.post("/generate")
async def generate_text(request: AIModelRequest):
    # By the time the code reaches here, request.temperature is guaranteed to be a float.
    # No manual if/else checks are needed.
    return {"status": "success", "length": len(request.prompt)}
```

## 2. Advanced Validation with `Field`

Type hints are useful, but usually, you need stricter business rules. For example, a temperature shouldn't just be _any_ float; it might need to be between 0.0 and 2.0. We use Pydantic's `Field` function to enforce these rules.

### A. Validating Numbers

You can enforce strict mathematical boundaries using the following arguments:

- `gt`: Greater than
- `ge`: Greater than or equal to
- `lt`: Less than
- `le`: Less than or equal to

```python
from pydantic import BaseModel, Field

class GenerationConfig(BaseModel):
    # Must be exactly between 0.0 and 2.0, defaults to 0.7 if not provided
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)

    # Must be at least 1, maximum 4096. The `...` means it is strictly required.
    max_tokens: int = Field(..., ge=1, le=4096)
```

### B. Validating Strings

You can restrict the length of strings or enforce specific patterns using Regular Expressions (Regex). This is highly recommended to prevent bad data or basic injection attempts.

```python
from pydantic import BaseModel, Field

class UserInput(BaseModel):
    # Enforce minimum and maximum length
    system_prompt: str = Field(..., min_length=10, max_length=500)

    # Enforce a specific pattern (e.g., Alphanumeric characters only, no spaces)
    project_code: str = Field(..., pattern="^[a-zA-Z0-9]+$")
```

## 3. Restricting Choices with `Enum`

When a field must be one of a few specific predefined options (like selecting an AI model engine from a dropdown), use Python's built-in `Enum` class. Pydantic natively understands and enforces it.

```python
from enum import Enum
from pydantic import BaseModel
from fastapi import FastAPI

app = FastAPI()

# 1. Define the exact allowed string values
class ModelEngine(str, Enum):
    GPT4 = "gpt-4"
    CLAUDE3 = "claude-3-opus"
    LLAMA3 = "llama-3-70b"

# 2. Use the Enum in your Pydantic model
class InferenceRequest(BaseModel):
    text: str
    engine: ModelEngine

@app.post("/process")
async def process_data(payload: InferenceRequest):
    # If the user sends engine="gpt-3", Pydantic will block the request automatically.
    if payload.engine == ModelEngine.GPT4:
        return {"routing_to": "OpenAI Servers"}
    return {"routing_to": "Other Servers"}
```

---

# Pydantic in FastAPI - Part 2: Nested Models and Complex Data Structures

In real-world APIs, you rarely just receive a flat JSON object with a few strings and numbers. Usually, you receive complex, deeply nested JSON data containing lists (arrays) and objects inside objects. Pydantic makes handling these incredibly easy.

## 1. Validating Lists (Arrays)

If your API expects a list of items, you simply use standard Python list typing. Pydantic will ensure that the incoming data is a list, and that every single item inside that list is of the correct type.

```python
from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI()

class BlogPayload(BaseModel):
    title: str
    # Expects a list of strings. If a user sends [1, 2, "AI"],
    # Pydantic will try to convert 1 and 2 to strings.
    tags: list[str]

    # You can also use Field to enforce rules on the list itself!
    # e.g., The list must contain at least 1 item, and no more than 5.
    categories: list[str] = Field(..., min_length=1, max_length=5)

@app.post("/blogs")
async def create_blog(payload: BlogPayload):
    return {"message": "Blog created", "tags_count": len(payload.tags)}
```

## 2. Nested Pydantic Models (Objects within Objects)

This is where Pydantic truly shines. If a JSON payload contains a nested object (like a user's address or a sub-configuration for an AI model), you create a separate Pydantic model for the nested part and use it as a type hint in your main model.

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

# 1. Define the "Child" model first
class DatabaseConfig(BaseModel):
    host: str
    port: int
    enable_ssl: bool = True

# 2. Define the "Parent" model
class AppConfiguration(BaseModel):
    app_name: str
    version: str
    # Use the child model as a type hint here
    db_settings: DatabaseConfig

@app.post("/config")
async def update_config(config: AppConfiguration):
    # You can access nested data using dot notation
    db_port = config.db_settings.port
    return {"connected_to": config.db_settings.host, "port": db_port}
```

_If a user sends a POST request without the `db_settings` block, or if `db_settings.port` is a string instead of an integer, Pydantic will instantly reject it with a detailed error._

## 3. Lists of Nested Models

You can combine the concepts above to validate an array of complex objects. This is highly common when doing batch processing (e.g., sending multiple prompts to an AI at once).

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

# A single item
class TrainingExample(BaseModel):
    prompt: str
    expected_completion: str

# The main payload expecting a list of items
class BatchTrainingRequest(BaseModel):
    dataset_name: str
    # A list where every item MUST be a valid 'TrainingExample' object
    examples: list[TrainingExample]

@app.post("/train/batch")
async def process_batch(request: BatchTrainingRequest):
    for example in request.examples:
        # We know for a fact that example.prompt exists and is a string
        print(f"Processing: {example.prompt}")

    return {"processed_items": len(request.examples)}
```

## 4. Dictionaries (Dynamic Keys)

Sometimes you don't know the exact names of the keys the user will send (for example, free-form metadata or environment variables), but you _do_ know the data types they should be. You can use Python's `dict` type hint.

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class SystemDeployment(BaseModel):
    server_id: str

    # We expect a dictionary where all keys are strings, and all values are floats.
    # Example JSON: {"cpu_limit": 4.5, "memory_gb": 16.0}
    resource_limits: dict[str, float]

@app.post("/deploy")
async def deploy_system(payload: SystemDeployment):
    return {"configured_limits": payload.resource_limits}
```

---

# Pydantic in FastAPI - Part 3: Custom Validation Logic

While built-in tools like `Field(gt=0)` or `min_length=5` are great, real-world backend engineering often requires complex business logic. What if you need to check if a username contains profanity? What if `end_date` must come after `start_date`?

For this, Pydantic v2 provides custom validator decorators: `@field_validator` and `@model_validator`.

## 1. Validating a Single Field (`@field_validator`)

You use `@field_validator` when you want to run custom Python code to validate or transform the data of one specific field.

### A. Basic Custom Validation (Rejecting Bad Data)

If your custom logic fails, you raise a `ValueError`. FastAPI will automatically catch this and return a beautiful `422 Unprocessable Entity` to the client with your exact error message.

```python
from fastapi import FastAPI
from pydantic import BaseModel, field_validator

app = FastAPI()

class UserRegistration(BaseModel):
    username: str
    email: str

    # 1. Point the validator to the specific field
    @field_validator('username')
    @classmethod
    def validate_username_not_admin(cls, value: str):
        # 2. Write your custom Python logic
        forbidden_names = ['admin', 'root', 'superuser']
        if value.lower() in forbidden_names:
            raise ValueError(f"The username '{value}' is reserved and cannot be used.")

        # 3. Always return the value if it passes!
        return value

@app.post("/register")
async def register_user(user: UserRegistration):
    return {"message": f"Welcome, {user.username}!"}
```

### B. Transforming Data (Data Cleaning)

Validators aren't just for blocking bad data; they are also excellent for silently cleaning up incoming data before your core logic runs.

```python
from pydantic import BaseModel, field_validator

class SearchQuery(BaseModel):
    query_text: str

    @field_validator('query_text')
    @classmethod
    def clean_query_text(cls, value: str):
        # Strip trailing/leading spaces and convert to lowercase automatically
        cleaned = value.strip().lower()

        if not cleaned:
            raise ValueError("Query cannot be empty or just whitespace.")

        return cleaned
```

## 2. Validating Multiple Fields Together (`@model_validator`)

Sometimes, a single field is valid on its own, but invalid when combined with another field. For example, validating that a password confirmation matches the password, or ensuring chronological dates.

You use `@model_validator(mode='after')` to inspect the entire model _after_ individual fields have been checked.

```python
from fastapi import FastAPI
from pydantic import BaseModel, model_validator
from datetime import date

app = FastAPI()

class DatasetQuery(BaseModel):
    dataset_name: str
    start_date: date
    end_date: date

    # Note: No specific field is mentioned in the decorator
    @model_validator(mode='after')
    def check_date_chronology(self):
        # 'self' now contains the fully parsed and validated individual fields
        if self.start_date > self.end_date:
            raise ValueError("The 'end_date' must occur after the 'start_date'.")

        # You must return 'self' at the end of a model_validator
        return self

@app.post("/query-data")
async def query_dataset(query: DatasetQuery):
    # We are 100% sure here that start_date is before or equal to end_date
    return {"status": "fetching", "range": f"{query.start_date} to {query.end_date}"}
```

## 3. Advanced: Conditional Validation (`@model_validator`)

In AI applications, sometimes providing one parameter means another parameter is required, or forbidden.

```python
from fastapi import FastAPI
from pydantic import BaseModel, model_validator

app = FastAPI()

class AIInferenceRequest(BaseModel):
    prompt: str
    # Both are optional individually
    use_custom_weights: bool = False
    custom_weights_id: str | None = None

    @model_validator(mode='after')
    def validate_custom_weights_logic(self):
        # If the user sets use_custom_weights to True, they MUST provide an ID
        if self.use_custom_weights and not self.custom_weights_id:
            raise ValueError("You must provide 'custom_weights_id' if 'use_custom_weights' is True.")

        # If they set it to False, they shouldn't be sending an ID
        if not self.use_custom_weights and self.custom_weights_id:
            raise ValueError("Cannot process 'custom_weights_id' when 'use_custom_weights' is False.")

        return self

@app.post("/infer")
async def run_inference(request: AIInferenceRequest):
    return {"status": "success", "using_custom": request.use_custom_weights}
```

---

# Pydantic in FastAPI - Part 4: Model Configurations, Aliases, and Documentation

Moving beyond validating individual fields, Pydantic allows you to control how the entire model behaves. This includes handling unexpected data, mapping weird JSON keys from external systems to clean Python variables, and generating beautiful documentation for your API.

## 1. Strict APIs: Forbidding Extra Data

By default, if a user sends extra JSON fields that are not defined in your Pydantic model, Pydantic simply ignores them. However, for strict APIs (especially AI configurations where typos can lead to expensive errors), you might want to reject the request entirely if unexpected data is present.

You do this using `model_config` and `ConfigDict`.

```python
from fastapi import FastAPI
from pydantic import BaseModel, ConfigDict

app = FastAPI()

class InferenceConfig(BaseModel):
    # This configuration tells Pydantic to throw an error if unknown fields are sent
    model_config = ConfigDict(extra='forbid')

    prompt: str
    temperature: float

@app.post("/generate")
async def generate_text(config: InferenceConfig):
    # If a user sends {"prompt": "Hi", "temperature": 0.7, "typo_field": True}
    # FastAPI will automatically return a 422 Error saying "Extra inputs are not permitted".
    return {"status": "success"}
```

## 2. Handling External Formats: Field Aliases

Python strictly uses `snake_case` for variables. But front-end developers usually send JSON in `camelCase`, and some APIs use hyphens (like `api-key`).

You can use the `alias` argument in `Field` to tell Pydantic: _"Look for this ugly name in the JSON, but let me use this clean name in my Python code."_

```python
from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI()

class UserProfile(BaseModel):
    # Look for 'firstName' in JSON, but name the variable 'first_name'
    first_name: str = Field(alias="firstName")

    # Look for 'x-api-key' in JSON, but name the variable 'api_key'
    api_key: str = Field(alias="x-api-key")

@app.post("/profile")
async def create_profile(profile: UserProfile):
    # Inside your code, you use standard Python formatting
    print(f"Creating profile for {profile.first_name}")

    # When sending data back, Pydantic will by default use your Python variable names.
    return {"saved_name": profile.first_name}
```

## 3. Populating FastAPI Docs: Adding Examples

One of FastAPI's best features is the automatic Swagger UI (`/docs`). To make this documentation truly professional, you should provide realistic examples of what the JSON payload should look like.

### A. Field-Level Examples

You can add examples to individual fields using the `examples` argument. This helps front-end teams understand exactly what you expect.

```python
from pydantic import BaseModel, Field

class ChatMessage(BaseModel):
    role: str = Field(
        ...,
        description="The role of the message author.",
        examples=["system", "user", "assistant"]
    )
    content: str = Field(
        ...,
        examples=["Translate the following text to French."]
    )
```

### B. Model-Level Examples (Advanced)

For complex AI requests, it is usually better to provide a complete JSON example for the entire model. You do this using `json_schema_extra` inside the `model_config`.

```python
from fastapi import FastAPI
from pydantic import BaseModel, ConfigDict

app = FastAPI()

class SummarizationRequest(BaseModel):
    document_text: str
    max_summary_length: int
    extract_keywords: bool

    # This injects a perfect, complete JSON example right into your /docs page
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "document_text": "The quick brown fox jumps over the lazy dog. It was a sunny day.",
                "max_summary_length": 50,
                "extract_keywords": True
            }
        }
    )

@app.post("/summarize")
async def summarize_doc(request: SummarizationRequest):
    return {"summary": "A fox jumped on a sunny day."}
```

## 4. Optional Fields vs. Default Values

A common point of confusion is how to make a field optional versus giving it a default value.

- **Optional but no default (must be explicitly sent as `null` or excluded):**
  Use `| None = None`. This means the value can be absent, but if we check it, it resolves to `None`.
- **Optional with a functional default:**
  If the user doesn't send it, Pydantic fills it in automatically.

```python
from pydantic import BaseModel
from typing import Optional

class DeploymentConfig(BaseModel):
    # Required: Must be in the JSON
    environment: str

    # Optional with default: If missing, Pydantic sets it to 1
    replica_count: int = 1

    # Truly Optional: Can be missing entirely. Resolves to None.
    # Good for optional IDs or flags that only apply sometimes.
    vpc_id: str | None = None
```

---

# Pydantic in FastAPI - Part 5: Response Models and Data Serialization

Up to this point, we have focused on validating _incoming_ data (Requests). However, as a backend developer, controlling the _outgoing_ data (Responses) is equally important. You need to ensure you are not accidentally leaking sensitive database fields (like passwords) and that your API outputs exactly match your documentation.

## 1. The Basics: Using `response_model`

Instead of just returning a Python dictionary from your route, you can tell FastAPI to filter the output through a Pydantic model using the `response_model` parameter in your route decorator.

This does two things:

1. It validates your outgoing data to ensure your code didn't break the contract.
2. It generates the correct schema for the Swagger UI documentation.

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class UserOut(BaseModel):
    id: int
    username: str
    email: str

# Mock database record (notice it has an extra field 'is_banned')
db_user = {"id": 1, "username": "ai_dev", "email": "dev@ai.com", "is_banned": False}

# We set response_model=UserOut
@app.get("/users/me", response_model=UserOut)
async def get_my_profile():
    # We return the whole database object
    return db_user
    # FastAPI automatically strips away 'is_banned' because it is not in UserOut!
    # The client only sees: {"id": 1, "username": "ai_dev", "email": "dev@ai.com"}
```

## 2. Intermediate: Hiding Sensitive Data

A common pattern is to have one model for creating a user (which requires a password), a database model (which stores the hashed password), and a response model (which hides the password completely).

```python
from fastapi import FastAPI
from pydantic import BaseModel, EmailStr # EmailStr requires `pip install pydantic[email]`

app = FastAPI()

# 1. Used for POST requests (Incoming)
class UserCreate(BaseModel):
    username: str
    password: str
    email: EmailStr

# 2. Used for GET/Responses (Outgoing)
class UserPublic(BaseModel):
    username: str
    email: EmailStr
    # Notice: No password field here!

@app.post("/users/", response_model=UserPublic)
async def create_user(user: UserCreate):
    # Imagine we hash the password and save to DB here
    saved_db_user = {
        "username": user.username,
        "email": user.email,
        "hashed_password": "hashed_12345"
    }

    # We return the DB object, but FastAPI filters it through UserPublic
    # The password is automatically hidden from the API response.
    return saved_db_user
```

## 3. Advanced: Partial Updates (PATCH) and `exclude_unset`

When building a `PATCH` endpoint (where a user can update just _one_ field, like changing only their email without touching their username), you run into a problem. If they don't send a username, Pydantic might complain it's missing, or overwrite the database with `None`.

To handle this cleanly, we make fields optional, and then use `exclude_unset=True` when dumping the data. This tells Pydantic to only return the fields the user _actually sent_ in the request, ignoring the defaults.

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

# All fields are optional because the user might only want to update one.
class UpdateProfileRequest(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    theme: str = "light"

# Mock DB Data
user_db = {"first_name": "Vijay", "last_name": "Simha", "theme": "dark"}

@app.patch("/profile")
async def update_profile(updates: UpdateProfileRequest):
    # If the user sends ONLY: {"first_name": "Ajay"}

    # 1. model_dump(exclude_unset=True) creates a dictionary of ONLY what was sent.
    # It ignores 'last_name' and the default 'theme' because the user didn't explicitly send them.
    update_data = updates.model_dump(exclude_unset=True)

    # update_data is now exactly: {"first_name": "Ajay"}

    # 2. Safely merge updates into the database
    for key, value in update_data.items():
        user_db[key] = value

    return {"status": "updated", "current_profile": user_db}
```

## 4. Advanced (Pydantic V2): Dynamic Outputs with `@computed_field`

Sometimes you want your API response to include a field that doesn't exist in your database, but is calculated on the fly based on other fields. In Pydantic V2, you use `@computed_field`.

```python
from fastapi import FastAPI
from pydantic import BaseModel, computed_field

app = FastAPI()

class ECommerceItem(BaseModel):
    name: str
    price: float
    tax_rate: float

    # This field is not required in the incoming request or the database.
    # It is calculated automatically whenever this model is sent out.
    @computed_field
    def total_price_with_tax(self) -> float:
        return round(self.price + (self.price * self.tax_rate), 2)

@app.get("/items/1", response_model=ECommerceItem)
async def get_item():
    # We fetch data from the DB that only has name, price, and tax_rate
    return {
        "name": "Mechanical Keyboard",
        "price": 100.0,
        "tax_rate": 0.08
    }
    # The client will receive:
    # {
    #   "name": "Mechanical Keyboard",
    #   "price": 100.0,
    #   "tax_rate": 0.08,
    #   "total_price_with_tax": 108.0  <-- Automatically computed!
    # }
```

---
