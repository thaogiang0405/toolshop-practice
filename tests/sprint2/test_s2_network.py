
"""Sprint 2 - Network interception tests."""

import json
import re

import pytest
from playwright.sync_api import expect

from pages.home_page import HomePage, PRODUCT_LIST


# S2.ROUTE01 - Chan anh, san pham van hien thi
@pytest.mark.ui
def test_s2_home_without_images(page):
    """Goal: verify homepage works without images.
    Precondition: product API is available.
    Expected: product names visible and images blocked."""
    blocked = []

    def block_image(route):
        blocked.append(route.request.url)
        route.abort()

    page.route(
        re.compile(r"\.(png|jpe?g|webp|avif|svg)(\?.*)?$"),
        block_image,
    )

    home = HomePage(page).open()

    expect(home.product_names.first).to_be_visible()

    assert blocked, "No image request was blocked"


# S2.ROUTE02 - Gia lap danh sach san pham rong
@pytest.mark.ui
def test_s2_empty_product_list(page):
    """Goal: verify the empty product state.
    Precondition: product API is mocked.
    Expected: no-results message and zero products."""
    empty_response = {
        "current_page": 1,
        "data": [],
        "per_page": 9,
        "total": 0,
        "last_page": 1,
    }

    page.route(
        PRODUCT_LIST,
        lambda route: route.fulfill(
            status=200,
            content_type="application/json",
            body=json.dumps(empty_response),
        ),
    )

    home = HomePage(page).open()

    expect(home.no_results).to_have_text(
        "There are no products found."
    )

    expect(home.product_names).to_have_count(0)
