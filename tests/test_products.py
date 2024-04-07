import datetime
import json
from time import sleep

from fastapi import FastAPI, status
from fastapi.testclient import TestClient

from models.users import UserRole


async def test_create_product_success(
    app: FastAPI,
    client: TestClient,
    create_test_user_and_get_token,
    get_product_from_db,
):
    product_url = app.url_path_for('create_product')
    user_id, auth_headers = await create_test_user_and_get_token(
        name='test_name',
        role=UserRole.SELLER
    )
    resp = client.post(
        url=product_url,
        json={
            'title': 'test_product',
            'cost': 100,
        },
        headers=auth_headers,
    )
    assert resp.status_code == status.HTTP_200_OK
    product_in_db = await get_product_from_db(resp.json()['id'])
    assert product_in_db[1] == 'test_product'
    assert product_in_db[2] == user_id
    assert product_in_db[3] == 100


async def test_create_product_fail_invalid_cost(
    app: FastAPI,
    client: TestClient,
    create_test_user_and_get_token,
    get_product_from_db,
):
    product_url = app.url_path_for('create_product')
    user_id, auth_headers = await create_test_user_and_get_token(
        name='test_name',
        role=UserRole.SELLER
    )
    resp = client.post(
        url=product_url,
        json={
            'title': 'test_product',
            'cost': -1,
        },
        headers=auth_headers,
    )
    assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


async def test_get_product_success(
    app: FastAPI,
    client: TestClient,
    create_product_in_db,
):
    product_id = await create_product_in_db('title', 100, 1)
    product_url = app.url_path_for('get_product', product_id=product_id)
    resp = client.get(url=product_url)
    assert resp.status_code == status.HTTP_200_OK
    body = resp.json()
    assert body['title'] == 'title'
    assert body['cost'] == 100
    assert body['seller_id'] == 1


async def test_get_product_fail_not_exists(
    app: FastAPI,
    client: TestClient,
):
    product_url = app.url_path_for('get_product', product_id=-1)
    resp = client.get(url=product_url)
    assert resp.status_code == status.HTTP_404_NOT_FOUND
    assert resp.json()['detail'] == "product doesn't exist"
