# FastAPI Endpoint Creation Checklist

## 1. Database Schema Check
- [ ] Review relevant database tables
- [ ] Note field names, types, and constraints
- [ ] Identify required vs optional fields
- [ ] Check foreign key relationships

## 2. Pydantic Models (schemas.py)
- [ ] Create request model (e.g., `EntityCreate`)
  - [ ] Match DB field names
  - [ ] Add appropriate Field validators
  - [ ] Include example values
  - [ ] Set proper constraints (min/max length, etc.)
- [ ] Create response model (e.g., `EntityResponse`)
  - [ ] Include all fields that should be returned
  - [ ] Add `from_attributes = True` in Config
  - [ ] Match types with DB schema

## 3. Router Endpoint
- [ ] Add proper HTTP method decorator
  - [ ] Set response_model
  - [ ] Add summary and description
  - [ ] Include security requirements
  - [ ] Document all possible responses (200, 401, 422, etc.)
- [ ] Define function parameters
  - [ ] Request body (if needed)
  - [ ] Dependencies (auth, db)
  - [ ] Path/query parameters (if needed)
- [ ] Add logging statements
- [ ] Include proper type hints

## 4. Documentation
- [ ] Add docstring to function
- [ ] Document request body schema in OpenAPI
- [ ] Include example values
- [ ] Document all response codes

## 5. Security
- [ ] Add authentication if required
- [ ] Add proper security scheme in OpenAPI
- [ ] Include authorization checks
- [ ] Add proper error responses

## 6. Example Usage
```python
@router.post(
    "/",
    response_model=EntityResponse,
    summary="Create new entity",
    responses={
        200: {"model": EntityResponse, "description": "Success"},
        401: {"description": "Not authenticated"},
        422: {"description": "Validation error"}
    },
    openapi_extra={
        "security": [{"bearerAuth": []}],
        "requestBody": {
            "content": {
                "application/json": {
                    "schema": {"$ref": "#/components/schemas/EntityCreate"}
                }
            },
            "required": True
        }
    }
)
async def create_entity(
    entity: EntityCreate,
    current_user: CurrentUser,
    db: Session = Depends(get_db)
):
    """Create a new entity for the authenticated user"""
    logger.info("create_entity endpoint called")
    return await entity_service.create_entity(db, entity, current_user.id)
```

## 7. Testing (Optional)
- [ ] Add unit tests
- [ ] Add integration tests
- [ ] Test with Swagger UI
- [ ] Test with actual client

## 8. Final Checks
- [ ] Verify OpenAPI schema is correct
- [ ] Check lock icon appears if authenticated
- [ ] Test example values work
- [ ] Verify error responses