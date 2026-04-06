# Q&A
___

## Do I need to import status from fastapi or starlette ?

**The short answer:** You should import it from `fastapi`. 

**The detailed answer:** Under the hood, you are actually importing the exact same thing. FastAPI is built directly on top of a microframework called **Starlette**. 

When the creator of FastAPI built the framework, he simply imported `status` from Starlette and exposed it in the FastAPI namespace for your convenience. 

If you look at the actual source code of FastAPI, it looks like this:
```python
# Inside fastapi/status.py
from starlette.status import *
```

### Why you should use `from fastapi import status`:

1. **Cleaner Imports:** It keeps your code organized. If you are already importing `FastAPI`, `HTTPException`, or `Depends`, you can just add `status` to the same line.
   ```python
   # Recommended: Clean and grouped
   from fastapi import FastAPI, HTTPException, status
   ```
2. **Mental Load:** You don't have to remember which features belong to Starlette and which belong to FastAPI. Just treat `fastapi` as your single source of truth.
3. **Future-Proofing:** While highly unlikely, if FastAPI ever decided to wrap or modify the status codes, importing from `fastapi` ensures your code won't break. 

So, while `from starlette import status` works perfectly fine and is technically correct, standardizing on `from fastapi import status` is the best practice for modern AI engineering backends.

___