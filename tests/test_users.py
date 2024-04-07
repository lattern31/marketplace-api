import datetime

from fastapi import FastAPI, status
from fastapi.testclient import TestClient

from models.users import UserRole


async def test_create_user_success(
    app: FastAPI,
    client: TestClient,
    get_user_from_db
):
    url = app.url_path_for('register_user')
    resp = client.post(url=url, json={
        'username': 'test_name',
        'role': UserRole.CUSTOMER,
        'password': 'test'
    })
    resp_body = resp.json()
    assert resp.status_code == status.HTTP_200_OK
    users = await get_user_from_db(resp_body['id'])
    assert len(users) == 1
    user = users[0]._asdict()
    assert user['username'] == 'test_name'
    assert user['role'] == UserRole.CUSTOMER.name
    assert isinstance(user['created_at'], datetime.datetime)


async def test_create_user_fail_duplicate_username(
    app: FastAPI,
    client: TestClient,
):
    url = app.url_path_for('register_user')
    resp = client.post(url=url, json={
        'username': 'test_name',
        'role': UserRole.CUSTOMER,
        'password': 'test'
    })
    assert resp.status_code == status.HTTP_200_OK
    resp = client.post(url=url, json={
        'username': 'test_name',
        'role': UserRole.CUSTOMER,
        'password': 'test'
    })
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert resp.json()['detail'] == 'username already taken'


async def test_create_user_fail_invalid_role(
    app: FastAPI,
    client: TestClient,
):
    url = app.url_path_for('register_user')
    invalid_role_name = f'{UserRole.CUSTOMER}some_text'
    resp = client.post(url=url, json={
        'username': 'test_name',
        'role': invalid_role_name,
        'password': 'test'
    })
    assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


async def test_user_get_my_profile_success(
    app: FastAPI,
    client: TestClient,
):
    reg_url = app.url_path_for('register_user')
    login_url = app.url_path_for('login_for_auth_token')
    get_me_url = app.url_path_for('get_my_profile')
    client.post(
        url=reg_url,
        json={
            'username': 'test_name',
            'role': UserRole.CUSTOMER,
            'password': 'test'
        }
    )
    form_data = {
        'username': 'test_name',
        'password': 'test'
    }
    resp = client.post(
        url=login_url,
        data=form_data,
    )
    assert resp.status_code == status.HTTP_200_OK
    access_token = resp.json()['access_token']
    resp = client.get(
        url=get_me_url,
        headers={'Authorization': f'Bearer {access_token}'}
    )
    assert resp.status_code == status.HTTP_200_OK
    user = resp.json()
    assert user['username'] == 'test_name'
    assert user['role'] == UserRole.CUSTOMER.value
