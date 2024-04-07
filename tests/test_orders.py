from fastapi import FastAPI, status
from fastapi.testclient import TestClient

from models.users import UserRole


async def test_create_order_success(
    app: FastAPI,
    client: TestClient,
    create_test_user_and_get_token,
    create_product_in_db,
    add_item_to_cart_in_db,
    get_order_from_db,
):
    customer_id, customer_auth_headers = await create_test_user_and_get_token(
        name='customer',
        role=UserRole.CUSTOMER
    )
    item_id = await create_product_in_db('title', 100, 1)
    await add_item_to_cart_in_db(customer_id, item_id, 1)
    create_order_url = app.url_path_for('create_order_handler')
    resp = client.post(
        url=create_order_url,
        headers=customer_auth_headers
    )
    assert resp.status_code == status.HTTP_200_OK
    order = await get_order_from_db(resp.json()['id'])
    assert len(order['content']) == 1
    assert order['content'][0]['product_id'] == item_id


async def test_create_order_fail_empty_cart(
    app: FastAPI,
    client: TestClient,
    create_test_user_and_get_token,
    get_order_from_db,
):
    customer_id, customer_auth_headers = await create_test_user_and_get_token(
        name='customer',
        role=UserRole.CUSTOMER
    )
    create_order_url = app.url_path_for('create_order_handler')
    resp = client.post(
        url=create_order_url,
        headers=customer_auth_headers
    )
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert resp.json()['detail'] == 'empty cart'


async def test_get_order_success(
    app: FastAPI,
    client: TestClient,
    create_test_user_and_get_token,
    create_product_in_db,
    create_order_in_db,
):
    customer_id, customer_auth_headers = await create_test_user_and_get_token(
        name='customer',
        role=UserRole.CUSTOMER
    )
    item_id = await create_product_in_db('title', 100, 1)
    order_id = await create_order_in_db(
        customer_id, [{'id': item_id, 'quantity': 1}]
    )
    get_order_url = app.url_path_for('get_order_handler', order_id=order_id)
    resp = client.get(url=get_order_url, headers=customer_auth_headers)
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()['id'] == order_id
    assert len(resp.json()['content']) == 1 
    assert resp.json()['content'][0]['id'] == item_id


async def test_get_my_orders_success(
    app: FastAPI,
    client: TestClient,
    create_test_user_and_get_token,
    create_product_in_db,
    create_order_in_db,
):
    customer_id, customer_auth_headers = await create_test_user_and_get_token(
        name='customer',
        role=UserRole.CUSTOMER
    )
    item_id = await create_product_in_db('title', 100, 1)
    order_id = await create_order_in_db(
        customer_id, [{'id': item_id, 'quantity': 1}]
    )
    order1_id = await create_order_in_db(
        customer_id, [{'id': item_id, 'quantity': 2}]
    )
    get_order_url = app.url_path_for('get_my_orders_handler')
    resp = client.get(url=get_order_url, headers=customer_auth_headers)
    assert resp.status_code == status.HTTP_200_OK
    body = resp.json()
    assert len(body) == 2
    assert body[0]['id'] == order_id
    assert body[1]['id'] == order1_id
    assert len(body[0]['content']) == 1
    assert len(body[1]['content']) == 1
    assert body[0]['content'][0]['id'] == item_id
    assert body[0]['content'][0]['quantity'] == 1
    assert body[1]['content'][0]['quantity'] == 2
