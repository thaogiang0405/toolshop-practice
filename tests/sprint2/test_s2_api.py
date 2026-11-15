
"""Sprint 2 - API tests using Playwright APIRequestContext."""

import json
from pathlib import Path

import pytest

from conftest import new_email, register_user, strong_password


DATA_FILE = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "search_keywords.json"
)

KEYWORDS = json.loads(DATA_FILE.read_text(encoding="utf-8"))


# S2.API01 - Kiem tra cau truc JSON san pham
@pytest.mark.api
@pytest.mark.smoke
def test_s2_products_json_structure(api):
    """Goal: verify product API contract.
    Precondition: products exist.
    Expected: HTTP 200 and valid product data."""
    response = api.get("/products")

    assert response.status == 200, response.text()

    body = response.json()

    for key in (
        "current_page",
        "data",
        "per_page",
        "total",
        "last_page",
    ):
        assert key in body

    products = body["data"]

    assert isinstance(products, list)
    assert 0 < len(products) <= body["per_page"]

    for product in products:
        assert isinstance(product["id"], (str, int))
        assert isinstance(product["name"], str)
        assert product["name"].strip()
        assert product["price"] > 0


# S2.API02 - Tim kiem tu file JSON
@pytest.mark.api
@pytest.mark.parametrize(
    "case",
    KEYWORDS,
    ids=[case["keyword"] for case in KEYWORDS],
)
def test_s2_search_products_from_json(api, case):
    """Goal: search with JSON-driven test data.
    Precondition: keywords have matching products.
    Expected: all returned names contain the keyword."""
    keyword = case["keyword"]
    expected = case["must_contain"]

    response = api.get(
        "/products/search",
        params={"q": keyword},
    )

    assert response.status == 200, response.text()

    products = response.json()["data"]

    assert products, "Search returned no products"

    for product in products:
        assert expected.lower() in product["name"].lower()


# S2.API03 - Kiem tra loi HTTP 4xx
@pytest.mark.api
@pytest.mark.parametrize(
    "endpoint, expected_status",
    [
        ("/users/me", 401),
        ("/products/does-not-exist", 404),
    ],
)
def test_s2_api_error_responses(api, endpoint, expected_status):
    """Goal: verify expected client errors.
    Precondition: no authorization for protected endpoint.
    Expected: HTTP 401 or 404."""
    response = api.get(endpoint)

    assert response.status == expected_status, response.text()


# S2.API04 - Truy cap tai khoan bang Bearer Token
@pytest.mark.api
def test_s2_authenticated_user_profile(
    api, auth_headers, test_user
):
    """Goal: access a protected API using a token.
    Precondition: test user is authenticated.
    Expected: HTTP 200 and matching email."""
    response = api.get(
        "/users/me",
        headers=auth_headers,
    )

    assert response.status == 200, response.text()

    body = response.json()

    assert body["email"] == test_user["email"]


# S2.API05 - Dang ky tai khoan bang HTTP POST
@pytest.mark.api
def test_s2_register_user_without_password_exposure(api):
    """Goal: register a user without exposing secrets.
    Precondition: use a unique email and strong password.
    Expected: HTTP 201 and no password in response."""
    email = new_email()
    password = strong_password()

    response = register_user(api, email, password)

    assert response.status == 201, response.text()

    body = response.json()

    assert "password" not in body
