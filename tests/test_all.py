from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)


def test_read_root():
    """Test the root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "FastAPI Vercel Template" in data["message"]


def test_health_check():
    """Test the health check endpoint"""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "timestamp" in data
    assert "version" in data


def test_echo():
    """Test the echo endpoint"""
    test_message = "Hello, FastAPI!"
    response = client.post("/api/v1/echo", json={"message": test_message})
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == test_message
    assert "timestamp" in data


def test_echo_validation():
    """Test echo endpoint validation"""
    # Test with empty message
    response = client.post("/api/v1/echo", json={"message": ""})
    assert response.status_code == 422

    # Test with missing message
    response = client.post("/api/v1/echo", json={})
    assert response.status_code == 422


def test_create_item():
    """Test creating a new item"""
    item_data = {
        "name": "Test Item",
        "description": "A test item",
        "price": 29.99,
        "tax": 2.99,
    }
    response = client.post("/api/v1/items", json=item_data)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == item_data["name"]
    assert data["description"] == item_data["description"]
    assert data["price"] == item_data["price"]
    assert data["tax"] == item_data["tax"]
    assert "id" in data
    assert "created_at" in data


def test_get_items():
    """Test getting all items"""
    response = client.get("/api/v1/items")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_get_items_pagination():
    """Test items pagination"""
    response = client.get("/api/v1/items?skip=0&limit=5")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) <= 5


def test_get_item_not_found():
    """Test getting a non-existent item"""
    response = client.get("/api/v1/items/999")
    assert response.status_code == 404


def test_create_user():
    """Test creating a new user"""
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "full_name": "Test User",
        "password": "testpassword123",
    }
    response = client.post("/api/v1/users", json=user_data)
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == user_data["username"]
    assert data["email"] == user_data["email"]
    assert data["full_name"] == user_data["full_name"]
    assert data["is_active"] is True
    assert "id" in data
    assert "created_at" in data
    # Password should not be in response
    assert "password" not in data


def test_create_user_duplicate_username():
    """Test creating user with duplicate username"""
    user_data = {
        "username": "duplicate",
        "email": "first@example.com",
        "password": "password123",
    }
    # First user creation should succeed
    response = client.post("/api/v1/users", json=user_data)
    assert response.status_code == 201

    # Second user with same username should fail
    user_data["email"] = "second@example.com"
    response = client.post("/api/v1/users", json=user_data)
    assert response.status_code == 400
    assert "Username already exists" in response.json()["detail"]


def test_create_user_duplicate_email():
    """Test creating user with duplicate email"""
    user_data = {
        "username": "user1",
        "email": "duplicate@example.com",
        "password": "password123",
    }
    # First user creation should succeed
    response = client.post("/api/v1/users", json=user_data)
    assert response.status_code == 201

    # Second user with same email should fail
    user_data["username"] = "user2"
    response = client.post("/api/v1/users", json=user_data)
    assert response.status_code == 400
    assert "Email already exists" in response.json()["detail"]


def test_get_users():
    """Test getting all users"""
    response = client.get("/api/v1/users")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_get_user_not_found():
    """Test getting a non-existent user"""
    response = client.get("/api/v1/users/999")
    assert response.status_code == 404


def test_item_crud_workflow():
    """Test complete CRUD workflow for items"""
    # Create an item
    item_data = {
        "name": "CRUD Test Item",
        "description": "Testing CRUD operations",
        "price": 15.50,
    }
    create_response = client.post("/api/v1/items", json=item_data)
    assert create_response.status_code == 201
    created_item = create_response.json()
    item_id = created_item["id"]

    # Get the item
    get_response = client.get(f"/api/v1/items/{item_id}")
    assert get_response.status_code == 200
    retrieved_item = get_response.json()
    assert retrieved_item["name"] == item_data["name"]

    # Update the item
    update_data = {
        "name": "Updated CRUD Test Item",
        "description": "Updated description",
        "price": 20.00,
    }
    update_response = client.put(f"/api/v1/items/{item_id}", json=update_data)
    assert update_response.status_code == 200
    updated_item = update_response.json()
    assert updated_item["name"] == update_data["name"]
    assert updated_item["price"] == update_data["price"]

    # Delete the item
    delete_response = client.delete(f"/api/v1/items/{item_id}")
    assert delete_response.status_code == 200

    # Verify item is deleted
    get_deleted_response = client.get(f"/api/v1/items/{item_id}")
    assert get_deleted_response.status_code == 404
