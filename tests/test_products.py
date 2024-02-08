import datetime
import json


async def test_create_product(client, get_product_from_db):
    resp = client.post('/products',
                       data=json.dumps({'name': 'test_name',
                                        'cost': 100}))
    resp_body = resp.json()
    assert resp.status_code == 200
    assert resp_body['name'] == 'test_name'
    products = await get_product_from_db(resp_body['name'])
    assert len(products) == 1
    product = products[0]._asdict()
    assert product['name'] == 'test_name'
    assert product['cost'] == 100
    assert isinstance(product['created_at'], datetime.datetime)


async def test_create_product_duplicate_name(client, get_product_from_db):
    resp = client.post('/products',
                       data=json.dumps({'name': 'test_name1',
                                        'cost': 100}))
    assert resp.status_code == 200
    resp = client.post('/products',
                       data=json.dumps({'name': 'test_name1',
                                        'cost': 200}))
    assert resp.status_code == 400
    assert resp.json()['detail'] == 'name already taken'


async def test_fetch_products(client, create_product_in_db):
    await create_product_in_db('create_test', 100)
    await create_product_in_db('create_test1', 200)
    resp = client.get('/products')
    resp_body = resp.json()
    resp = client.get('/products')
    resp_body = resp.json()
    assert resp.status_code == 200
    assert len(resp_body) == 2
    assert resp_body[0]['name'] == 'create_test'
    assert resp_body[0]['cost'] == 100
    assert resp_body[1]['name'] == 'create_test1'
    assert resp_body[1]['cost'] == 200
    resp = client.get('/products/?name=1')
    assert resp.status_code == 200
    resp_body = resp.json()
    assert len(resp_body) == 1
    assert resp_body[0]['name'] == 'create_test1'
    assert resp_body[0]['cost'] == 200
