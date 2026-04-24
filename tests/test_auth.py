def test_register(client):
    response = client.post("/auth/register", json={
        "email": "user1@example.com",
        "password": "securepassword123",
    })
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_register_duplicate_email(client):
    payload = {"email": "duplicate@example.com", "password": "securepassword123"}
    client.post("/auth/register", json=payload)
    response = client.post("/auth/register", json=payload)
    assert response.status_code == 400


def test_login_returns_token(client):
    client.post("/auth/register", json={
        "email": "loginuser@example.com",
        "password": "securepassword123",
    })
    response = client.post("/auth/login", json={
        "email": "loginuser@example.com",
        "password": "securepassword123",
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client):
    client.post("/auth/register", json={
        "email": "wrongpass@example.com",
        "password": "securepassword123",
    })
    response = client.post("/auth/login", json={
        "email": "wrongpass@example.com",
        "password": "notthepassword",
    })
    assert response.status_code == 401
