from fastapi import FastAPI, status
from fastapi.testclient import TestClient

from models.users import UserRole


async def test_get_cart_success(
    app: FastAPI,
    client: TestClient,
    create_test_user_and_get_token,
    create_product_in_db,
    add_item_to_cart_in_db,
):
    customer_id, customer_auth_headers = await create_test_user_and_get_token(
        name='customer',
        role=UserRole.CUSTOMER
    )
    cart_get_content_url = app.url_path_for('get_cart_handler')
    await add_item_to_cart_in_db(
        customer_id, (await create_product_in_db('title', 100, 1)), 2)
    resp = client.get(
        url=cart_get_content_url,
        headers=customer_auth_headers
    )
    assert resp.status_code == status.HTTP_200_OK
    item = resp.json()['content'][0]
    assert item['title'] == 'title'
    assert item['cost'] == 100
    assert item['seller_id'] == 1
    assert item['quantity'] == 2


async def test_add_item_to_cart_success(
    app: FastAPI,
    client: TestClient,
    create_test_user_and_get_token,
    create_product_in_db,
    get_cart_from_db,
):
    cart_add_item_url = app.url_path_for('add_item_to_cart_handler')
    seller_id, _ = await create_test_user_and_get_token(
        name='seller',
        role=UserRole.SELLER
    )
    customer_id, customer_auth_headers = await create_test_user_and_get_token(
        name='customer',
        role=UserRole.CUSTOMER
    )
    product_id = await create_product_in_db(
        title='product', cost=100, seller_id=seller_id
    )
    resp = client.post(
        url=cart_add_item_url,
        json={'product_id': product_id},
        headers=customer_auth_headers
    )
    cart = await get_cart_from_db(customer_id)
    assert cart[0]['user_id'] == customer_id
    assert cart[0]['product_id'] == product_id
    assert cart[0]['quantity'] == 1
    resp = client.post(
        url=cart_add_item_url,
        json={'product_id': product_id},
        headers=customer_auth_headers
    )
    cart = await get_cart_from_db(customer_id)
    assert cart[0]['quantity'] == 2
    assert resp.status_code == status.HTTP_200_OK


async def test_delete_item_from_cart_success(
    app: FastAPI,
    client: TestClient,
    create_test_user_and_get_token,
    create_product_in_db,
    get_cart_from_db,
    add_item_to_cart_in_db,
):
    customer_id, customer_auth_headers = await create_test_user_and_get_token(
        name='customer',
        role=UserRole.CUSTOMER
    )
    cart_delete_item_url = app.url_path_for('remove_item_from_cart_handler')
    item_id = await create_product_in_db('title', 100, 1)
    item1_id = await create_product_in_db('title1', 200, 1)
    await add_item_to_cart_in_db(customer_id, item_id, 2)
    await add_item_to_cart_in_db(customer_id, item1_id, 2)
    resp = client.delete(
        url=cart_delete_item_url,
        headers=customer_auth_headers,
        params={'product_id': item_id}
    )
    assert resp.status_code == status.HTTP_200_OK
    cart = await get_cart_from_db(customer_id)
    assert len(cart) == 1
    assert cart[0]['product_id'] == item1_id
