from fastapi import APIRouter, HTTPException, Query, Path
from typing import List
import logging

from .schemas import (
    HealthResponse,
    EchoRequest,
    EchoResponse,
    ItemCreate,
    ItemResponse,
    UserCreate,
    UserResponse,
)

router = APIRouter()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# In-memory storage for demo purposes
items_db = []
users_db = []
next_item_id = 1
next_user_id = 1


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse()


@router.post("/echo", response_model=EchoResponse)
async def echo(request: EchoRequest):
    """Echo endpoint that returns the sent message"""
    logger.info(f"Echo request: {request.message}")
    return EchoResponse(message=request.message)


@router.get("/items", response_model=List[ItemResponse])
async def get_items(
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of items to return"),
):
    """Get all items with pagination"""
    logger.info(f"Getting items with skip={skip}, limit={limit}")
    return items_db[skip : skip + limit]


@router.post("/items", response_model=ItemResponse, status_code=201)
async def create_item(item: ItemCreate):
    """Create a new item"""
    global next_item_id

    logger.info(f"Creating item: {item.name}")

    new_item = ItemResponse(
        id=next_item_id,
        name=item.name,
        description=item.description,
        price=item.price,
        tax=item.tax,
    )

    items_db.append(new_item)
    next_item_id += 1

    return new_item


@router.get("/items/{item_id}", response_model=ItemResponse)
async def get_item(item_id: int = Path(..., gt=0, description="The ID of the item")):
    """Get a specific item by ID"""
    logger.info(f"Getting item with ID: {item_id}")

    for item in items_db:
        if item.id == item_id:
            return item

    raise HTTPException(status_code=404, detail="Item not found")


@router.put("/items/{item_id}", response_model=ItemResponse)
async def update_item(
    item_id: int = Path(..., gt=0, description="The ID of the item"),
    item_update: ItemCreate = None,
):
    """Update an existing item"""
    logger.info(f"Updating item with ID: {item_id}")

    for i, item in enumerate(items_db):
        if item.id == item_id:
            updated_item = ItemResponse(
                id=item_id,
                name=item_update.name,
                description=item_update.description,
                price=item_update.price,
                tax=item_update.tax,
                created_at=item.created_at,
            )
            items_db[i] = updated_item
            return updated_item

    raise HTTPException(status_code=404, detail="Item not found")


@router.delete("/items/{item_id}")
async def delete_item(item_id: int = Path(..., gt=0, description="The ID of the item")):
    """Delete an item"""
    logger.info(f"Deleting item with ID: {item_id}")

    for i, item in enumerate(items_db):
        if item.id == item_id:
            items_db.pop(i)
            return {"message": f"Item {item_id} deleted successfully"}

    raise HTTPException(status_code=404, detail="Item not found")


@router.post("/users", response_model=UserResponse, status_code=201)
async def create_user(user: UserCreate):
    """Create a new user"""
    global next_user_id

    logger.info(f"Creating user: {user.username}")

    # Check if username already exists
    for existing_user in users_db:
        if existing_user.username == user.username:
            raise HTTPException(status_code=400, detail="Username already exists")

    # Check if email already exists
    for existing_user in users_db:
        if existing_user.email == user.email:
            raise HTTPException(status_code=400, detail="Email already exists")

    new_user = UserResponse(
        id=next_user_id,
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        is_active=True,
    )

    users_db.append(new_user)
    next_user_id += 1

    return new_user


@router.get("/users", response_model=List[UserResponse])
async def get_users(
    skip: int = Query(0, ge=0, description="Number of users to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of users to return"),
):
    """Get all users with pagination"""
    logger.info(f"Getting users with skip={skip}, limit={limit}")
    return users_db[skip : skip + limit]


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int = Path(..., gt=0, description="The ID of the user")):
    """Get a specific user by ID"""
    logger.info(f"Getting user with ID: {user_id}")

    for user in users_db:
        if user.id == user_id:
            return user

    raise HTTPException(status_code=404, detail="User not found")
