# Pydantic in FastAPI - Part 6: Swagger UI and OpenAPI Configurations

FastAPI automatically generates an interactive API documentation page (Swagger UI) at the `/docs` endpoint. This is powered by the OpenAPI standard. As an AI Engineer, having a beautifully documented API is critical because data scientists, frontend developers, and external clients need to know exactly how to interact with your machine learning models.

You can configure this documentation at three levels: The Application, The Route, and The Pydantic Model.

## 1. Application-Level Configuration

Before looking at models, you should brand your overall Swagger UI page. You do this when you initialize the `FastAPI` object.

```python
from fastapi import FastAPI

# These details appear at the very top of your /docs page
app = FastAPI(
    title="Enterprise AI Platform API",
    description="""
    This API provides access to our suite of machine learning models.

    ### Core Features:
    * **Text Generation**: Powered by custom LLMs.
    * **Sentiment Analysis**: Real-time text classification.
    """,
    version="2.1.0",
    contact={
        "name": "AI Platform Team",
        "email": "ai-support@company.com",
        "url": "https://internal.company.com/ai-docs",
    },
    license_info={
        "name": "Proprietary - Internal Use Only",
    }
)
```

## 2. Route-Level Configuration

You can organize your Swagger UI by grouping related endpoints together and providing clear summaries for each HTTP action.

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class InferenceRequest(BaseModel):
    text: str

# 1. tags: Groups endpoints into sections in the Swagger UI sidebar.
# 2. summary: A short title for the endpoint.
# 3. response_description: Documents the HTTP 200 response block.
# 4. Docstrings ("""): Automatically become the detailed description body!

@app.post(
    "/v1/models/sentiment",
    tags=["Sentiment Analysis Models"],
    summary="Run Sentiment Inference",
    response_description="Returns a JSON object with the predicted sentiment score."
)
async def analyze_sentiment(payload: InferenceRequest):
    """
    Analyzes the sentiment of the provided text.

    **Warning:** This endpoint currently only supports English text up to 512 tokens.
    Passing longer text will result in truncation.
    """
    return {"sentiment": "positive", "score": 0.98}
```

## 3. Field-Level Configuration (Pydantic `Field`)

This is where Pydantic directly controls the Swagger UI. When a developer looks at the "Schemas" section of your docs, they will see these exact descriptions and examples.

```python
from pydantic import BaseModel, Field

class LLMGenerationConfig(BaseModel):
    # 1. Title and Description: Explains the field clearly
    prompt: str = Field(
        ...,
        title="Input Prompt",
        description="The system instruction or user query to send to the LLM."
    )

    # 2. Examples: Fills in the Swagger UI input boxes with realistic data
    temperature: float = Field(
        0.7,
        ge=0.0,
        le=2.0,
        description="Controls the randomness of the output.",
        examples=[0.2, 0.7, 1.5]
    )

    # 3. Deprecation: Visually crosses out the field in Swagger UI!
    # Useful when migrating AI models to newer parameters.
    max_length: int | None = Field(
        default=None,
        description="Legacy parameter. Use 'max_tokens' instead.",
        deprecated=True
    )
```

## 4. Model-Level Configuration (`json_schema_extra`)

While field-level examples are great, it is usually much better to provide one perfect, complete JSON payload example for the entire request. This allows developers to simply click "Try it out" in Swagger UI and hit "Execute" without typing anything.

You do this using Pydantic V2's `model_config`.

```python
from fastapi import FastAPI
from pydantic import BaseModel, Field, ConfigDict

app = FastAPI()

class ImageGenerationRequest(BaseModel):
    prompt: str = Field(..., min_length=10)
    negative_prompt: str | None = None
    aspect_ratio: str = "1:1"
    steps: int = Field(30, ge=10, le=100)

    # Injects a custom JSON example directly into the Swagger UI request body
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "prompt": "A futuristic city at sunset, cyberpunk style, neon lights",
                "negative_prompt": "blurry, low resolution, poorly drawn",
                "aspect_ratio": "16:9",
                "steps": 50
            }
        }
    )

@app.post("/generate-image", tags=["Image Models"])
async def generate_image(request: ImageGenerationRequest):
    return {"status": "processing", "job_id": "img-12345"}
```

## 5. Deprecating Entire Endpoints

If you are releasing a new version of an AI model and want to phase out the old one, you can mark the entire endpoint as deprecated. It will show up faded and crossed out in the Swagger UI, warning users not to build new integrations with it.

```python
from fastapi import FastAPI

app = FastAPI()

@app.post(
    "/v1/models/classifier",
    tags=["Legacy Models"],
    deprecated=True, # This crosses out the endpoint in the docs!
    summary="Legacy Text Classifier (Deprecated)"
)
async def old_classifier():
    """
    **DEPRECATED**: Please migrate to `/v2/models/classifier`.
    This endpoint will be removed on Dec 31st.
    """
    return {"warning": "deprecated", "result": "mock"}
```
