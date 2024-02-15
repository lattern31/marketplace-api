import datetime
import json


async def test_create_product(client, get_product_from_db):
    resp = client.post('/products',
                       content=json.dumps({'title': 'test_name',
                                        'cost': 100}))
    resp_body = resp.json()
    assert resp.status_code == 200
    products = await get_product_from_db(resp_body['id'])
    assert len(products) == 1
    product = products[0]._asdict()
    assert product['title'] == 'test_name'
    assert product['cost'] == 100
    assert isinstance(product['created_at'], datetime.datetime)


async def test_fetch_products(client, create_product_in_db):
    await create_product_in_db('create_test', 100)
    await create_product_in_db('create_test1', 200)
    resp = client.get('/products')
    resp_body = resp.json()
    resp = client.get('/products')
    resp_body = resp.json()
    assert resp.status_code == 200
    assert len(resp_body) == 2
    assert resp_body[0]['title'] == 'create_test'
    assert resp_body[0]['cost'] == 100
    assert resp_body[1]['title'] == 'create_test1'
    assert resp_body[1]['cost'] == 200
    resp = client.get('/products/?title=1')
    assert resp.status_code == 200
    resp_body = resp.json()
    assert len(resp_body) == 1
    assert resp_body[0]['title'] == 'create_test1'
    assert resp_body[0]['cost'] == 200
