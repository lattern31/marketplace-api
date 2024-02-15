import json
import datetime


async def test_create_user(client, get_user_from_db):
    resp = client.post('/users', content=json.dumps({'username': 'test_name'}))
    resp_body = resp.json()
    assert resp.status_code == 200
    users = await get_user_from_db(resp_body['id'])
    assert len(users) == 1
    user = users[0]._asdict()
    assert user['username'] == 'test_name'
    assert isinstance(user['created_at'], datetime.datetime)


async def test_create_user_duplicate_username(client, get_user_from_db):
    resp = client.post('/users', content=json.dumps({'username': 'test_name1'}))
    assert resp.status_code == 200
    resp = client.post('/users', content=json.dumps({'username': 'test_name1'}))
    assert resp.status_code == 400
    assert resp.json()['detail'] == 'username already taken'


async def test_fetch_users(client, create_user_in_db):
    await create_user_in_db('create_test')
    await create_user_in_db('create_test1')
    resp = client.get('/users')
    resp_body = resp.json()
    assert resp.status_code == 200
    assert len(resp_body) == 2
    assert resp_body[0]['username'] == 'create_test'
    assert resp_body[1]['username'] == 'create_test1'
    resp = client.get('/users/?username=1')
    assert resp.status_code == 200
    resp_body = resp.json()
    assert len(resp_body) == 1
    assert resp_body[0]['username'] == 'create_test1'
