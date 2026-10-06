def test_login_me_and_logout(client):
    bad = client.post(
        "/api/v1/auth/login", json={"email": "student@example.com", "password": "wrong"}
    )
    assert bad.status_code == 401
    login = client.post(
        "/api/v1/auth/login",
        json={"email": "student@example.com", "password": "Password123!"},
    )
    assert login.status_code == 200
    assert login.json()["account"]["aws_account_id"] == "610867948442"
    assert client.get("/api/v1/auth/me").status_code == 200
    assert client.post("/api/v1/auth/logout").status_code == 204
    assert client.get("/api/v1/auth/me").status_code == 401
