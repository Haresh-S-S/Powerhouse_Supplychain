import pytest
from fastapi.testclient import TestClient


def test_signup_success(client: TestClient):
    payload = {
        "email": "owner@powerhouse.in",
        "full_name": "Mohith K",
        "password": "SecurePassword123!",
        "phone_number": "+91 98765 43210"
    }
    response = client.post("/api/v1/auth/signup", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == "owner@powerhouse.in"
    assert data["user"]["full_name"] == "Mohith K"
    assert data["onboarding_completed"] is False


def test_signup_duplicate_email(client: TestClient):
    payload = {
        "email": "duplicate@powerhouse.in",
        "full_name": "Test User",
        "password": "Password123!"
    }
    res1 = client.post("/api/v1/auth/signup", json=payload)
    assert res1.status_code == 201

    res2 = client.post("/api/v1/auth/signup", json=payload)
    assert res2.status_code == 400
    assert "already exists" in res2.json()["detail"].lower()


def test_login_success(client: TestClient):
    # First signup
    signup_payload = {
        "email": "login_test@powerhouse.in",
        "full_name": "Login Tester",
        "password": "CorrectPassword123"
    }
    client.post("/api/v1/auth/signup", json=signup_payload)

    # Login with correct password
    login_payload = {
        "email": "login_test@powerhouse.in",
        "password": "CorrectPassword123"
    }
    response = client.post("/api/v1/auth/login", json=login_payload)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user"]["email"] == "login_test@powerhouse.in"


def test_login_invalid_password(client: TestClient):
    signup_payload = {
        "email": "wrong_pw@powerhouse.in",
        "full_name": "Wrong Password",
        "password": "CorrectPassword123"
    }
    client.post("/api/v1/auth/signup", json=signup_payload)

    login_payload = {
        "email": "wrong_pw@powerhouse.in",
        "password": "WrongPassword!"
    }
    response = client.post("/api/v1/auth/login", json=login_payload)
    assert response.status_code == 401


def test_login_non_existent_user(client: TestClient):
    login_payload = {
        "email": "does_not_exist@powerhouse.in",
        "password": "AnyPassword"
    }
    response = client.post("/api/v1/auth/login", json=login_payload)
    assert response.status_code == 401


def test_me_unauthorized(client: TestClient):
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401


def test_me_authorized(client: TestClient):
    signup_payload = {
        "email": "me_test@powerhouse.in",
        "full_name": "Auth Status Tester",
        "password": "Password123"
    }
    signup_res = client.post("/api/v1/auth/signup", json=signup_payload)
    token = signup_res.json()["access_token"]

    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["authenticated"] is True
    assert data["user"]["email"] == "me_test@powerhouse.in"
    assert data["onboarding_completed"] is False


def test_user_business_profile_isolation(client: TestClient):
    # User A
    user_a = client.post("/api/v1/auth/signup", json={
        "email": "usera@powerhouse.in",
        "full_name": "User Alpha",
        "password": "Password123"
    }).json()
    token_a = user_a["access_token"]

    # User B
    user_b = client.post("/api/v1/auth/signup", json={
        "email": "userb@powerhouse.in",
        "full_name": "User Beta",
        "password": "Password123"
    }).json()
    token_b = user_b["access_token"]

    # User A creates a business profile
    create_profile_payload = {
        "business_name": "Alpha Garments",
        "business_type": "Private Limited Company",
        "industry": "Textile",
        "company_size": "Small",
        "employee_count": 25,
        "city": "Tiruppur",
        "state": "Tamil Nadu",
        "business_category": "clothing_textile",
        "onboarding_completed": True
    }
    create_res = client.post(
        "/api/v1/business-profile",
        json=create_profile_payload,
        headers={"Authorization": f"Bearer {token_a}"}
    )
    assert create_res.status_code == 201
    profile_id = create_res.json()["id"]

    # User A sees it under /user/me
    a_profiles = client.get(
        "/api/v1/business-profile/user/me",
        headers={"Authorization": f"Bearer {token_a}"}
    ).json()
    assert len(a_profiles) == 1
    assert a_profiles[0]["id"] == profile_id

    # User B does NOT see User A's profile under /user/me
    b_profiles = client.get(
        "/api/v1/business-profile/user/me",
        headers={"Authorization": f"Bearer {token_b}"}
    ).json()
    assert len(b_profiles) == 0

    # User A's /auth/me reflects onboarding_completed = True
    me_a = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token_a}"}
    ).json()
    assert me_a["onboarding_completed"] is True
    assert me_a["active_business"]["business_name"] == "Alpha Garments"
