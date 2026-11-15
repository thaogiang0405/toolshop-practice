
"""Sprint 2 - UI automation tests."""

import pytest
from playwright.sync_api import expect

from pages.home_page import HomePage
from pages.contact_page import ContactPage

# S2.UI01 - Tim san pham theo tu khoa
@pytest.mark.ui
@pytest.mark.smoke
def test_s2_search_products_by_keyword(page):
    """Goal: search for products.
    Precondition: homepage is available.
    Expected: returned product names contain the keyword."""
    home = HomePage(page).open().search("pliers")

    expect(home.search_completed).to_be_visible()

    names = home.product_names.all_inner_texts()

    assert names, "No products returned"
    assert all("pliers" in name.lower() for name in names)


# S2.UI02 - Tim kiem khong co ket qua
@pytest.mark.ui
def test_s2_search_unknown_keyword(page):
    """Goal: search for a nonexistent product.
    Precondition: homepage is available.
    Expected: no products message and zero products."""
    home = HomePage(page).open().search("zzz-no-such-tool")

    expect(home.no_results).to_have_text(
        "There are no products found."
    )

    expect(home.product_names).to_have_count(0)


# S2.UI03 - Xem chi tiet san pham
@pytest.mark.ui
def test_s2_view_product_detail(page):
    """Goal: view product details.
    Precondition: Claw Hammer exists.
    Expected: product detail shows the correct name."""
    home = HomePage(page).open()

    product = home.open_product("Claw Hammer")

    expect(product.name).to_have_text("Claw Hammer")


# S2.UI04 - Them 3 san pham vao gio hang
@pytest.mark.ui
def test_s2_add_product_to_cart(page):
    """Goal: add a product to the cart.
    Precondition: Claw Hammer exists.
    Expected: success toast and cart quantity of 3."""
    home = HomePage(page).open()

    product = home.open_product("Claw Hammer")

    product.add_to_cart(quantity=3)

    expect(product.toast).to_contain_text(
        "Product added to shopping cart"
    )

    expect(product.cart_quantity).to_have_text("3")


# S2.UI05 - Kiem tra thanh tien gio hang
@pytest.mark.ui
def test_s2_cart_total_price(page):
    """Goal: verify cart calculations.
    Precondition: Combination Pliers exists.
    Expected: line total equals unit price times quantity."""
    product = HomePage(page).open().open_product(
        "Combination Pliers"
    )

    unit_price = product.price()

    product.add_to_cart(quantity=2)

    cart = product.go_to_cart()

    expect(cart.product_titles).to_have_count(1)

    assert cart.line_totals() == [
        pytest.approx(unit_price * 2)
    ]

    assert cart.total_value() == pytest.approx(
        sum(cart.line_totals())
    )


# S2.UI06 - Tiep tuc mua sam
@pytest.mark.ui
def test_s2_continue_shopping(page):
    """Goal: return to homepage from the cart.
    Precondition: Hammer has been added to the cart.
    Expected: product list becomes visible again."""
    product = HomePage(page).open().open_product("Hammer")

    product.add_to_cart()

    cart = product.go_to_cart()

    expect(cart.product_titles.first).to_have_text("Hammer")

    cart.continue_shopping.click()

    expect(
        HomePage(page).product_names.first
    ).to_be_visible()
 
import re

from pages.login_page import LoginPage


# S2.UI07 - Dang nhap sai mat khau
@pytest.mark.ui
def test_s2_login_wrong_password(page):
    """Goal: reject invalid credentials.
    Precondition: use an email without an account.
    Expected: error message and login page remains open."""
    login = LoginPage(page).open().login(
        "nobody-here@example.com",
        "Wrong-Password-123"
    )

    expect(login.error).to_contain_text(
        "Invalid email or password"
    )

    expect(page).to_have_url(re.compile(r"/auth/login$"))


# S2.UI08 - Kiem tra validation khi bo trong form
@pytest.mark.ui
def test_s2_login_empty_form(page):
    """Goal: validate required login fields.
    Precondition: email and password are empty.
    Expected: both required-field errors appear."""
    login = LoginPage(page).open()

    login.submit_button.click()

    expect(login.email_error).to_contain_text(
        "Email is required"
    )

    expect(login.password_error).to_contain_text(
        "Password is required"
    )


# S2.UI09 - Sap xep gia tang dan
@pytest.mark.ui
def test_s2_sort_price_ascending(page):
    """Goal: sort products by ascending price.
    Precondition: products are available.
    Expected: prices are sorted from low to high."""
    home = HomePage(page).open()

    home.sort_by("price,asc")

    expect(home.sorting_completed).to_be_visible()

    prices = home.prices()

    assert prices, "No product prices found"
    assert prices == sorted(prices)


# S2.UI10 - Sap xep gia giam dan
@pytest.mark.ui
def test_s2_sort_price_descending(page):
    """Goal: sort products by descending price.
    Precondition: products are available.
    Expected: prices are sorted from high to low."""
    home = HomePage(page).open()

    home.sort_by("price,desc")

    expect(home.sorting_completed).to_be_visible()

    prices = home.prices()

    assert prices, "No product prices found"
    assert prices == sorted(prices, reverse=True)


# S2.UI11 - Kiem tra cac truong trong form lien he
@pytest.mark.ui
def test_s2_contact_form_fields_visible(page):
    """Goal: verify contact form fields.
    Precondition: contact page is available.
    Expected: all required form controls are visible."""
    contact = ContactPage(page).open()

    expect(contact.first_name).to_be_visible()
    expect(contact.last_name).to_be_visible()
    expect(contact.email).to_be_visible()
    expect(contact.subject).to_be_visible()
    expect(contact.message).to_be_visible()
    expect(contact.attachment).to_be_visible()
    expect(contact.submit_button).to_be_visible()


# S2.UI12 - Kiem tra validation cua form lien he
@pytest.mark.ui

@pytest.mark.ui
def test_s2_contact_empty_form_validation(page):
    """Goal: reject an empty contact form.
    Precondition: all fields are empty.
    Expected: validation errors appear."""
    contact = ContactPage(page).open()

    contact.submit()

    # Kiem tra loi khi chua chon chu de
    expect(
        page.get_by_test_id("subject-error")
    ).to_be_visible()

    # Kiem tra loi khi chua nhap noi dung
    expect(
        page.get_by_test_id("message-error")
    ).to_be_visible()
