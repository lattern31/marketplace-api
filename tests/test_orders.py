import json
import datetime

import httpx


async def test_create_order(client, get_order_from_db, create_user_in_db):
    user_id = (await create_user_in_db('test_username'))

    resp = client.post('/orders', data=json.dumps({'user_id': user_id}))
    resp_body = resp.json()
    assert resp.status_code == 200
    order = await get_order_from_db(resp_body['id'])
    assert order['user_id'] == user_id
    assert isinstance(order['created_at'], datetime.datetime)

    resp = client.post('/orders', data=json.dumps({'user_id': user_id+1}))
    assert resp.status_code == 404
    assert resp.json()['detail'] == "user doesn't exist"


async def test_get_order(client, create_order_in_db, create_user_in_db):
    user_id = await create_user_in_db('test_username')
    order_id = await create_order_in_db(user_id)
    resp = client.get(f'/orders/{order_id}')
    resp_body = resp.json()
    assert resp.status_code == 200
    assert resp_body['user_id'] == user_id


async def test_add_item_to_order(client, create_order_in_db,
                                 create_user_in_db, create_product_in_db,
                                 get_order_from_db):
    user_id = await create_user_in_db('test_username')
    order_id = await create_order_in_db(user_id)

    product_name = await create_product_in_db('test_product', 150)
    resp = client.post(f'/orders/{order_id}/item',
                       data=json.dumps({'product_name': product_name,
                                        'quantity': 2}))
    print(resp.json())
    assert resp.status_code == 200
    order = await get_order_from_db(order_id)
    assert order['content'][0]['product_name'] == product_name
    assert order['content'][0]['quantity'] == 2

    product_name1 = await create_product_in_db('test_product1', 300)
    resp = client.post(f'/orders/{order_id}/item',
                       data=json.dumps({'product_name': product_name1,
                                        'quantity': 3}))
    assert resp.status_code == 200
    order = await get_order_from_db(order_id)
    print(order)
    assert order['content'][1]['product_name'] == product_name1
    assert order['content'][1]['quantity'] == 3

    resp = client.post(f'/orders/{order_id}/item',
                       data=json.dumps({'product_name': product_name,
                                        'quantity': 5}))
    assert resp.status_code == 200
    order = await get_order_from_db(order_id)
    assert len(order['content']) == 2
    assert order['content'][0]['quantity'] == 7

    resp = client.post(f'/orders/{order_id}/item',
                       data=json.dumps({'product_name': product_name,
                                        'quantity': 0}))
    assert resp.status_code == 400
    assert resp.json()['detail'] == "quantity can't be less than or equal to 0"

    resp = client.post(f'/orders/{order_id}/item',
                       data=json.dumps({'product_name': 'not existing name',
                                        'quantity': 1}))
    assert resp.status_code == 404
    assert resp.json()['detail'] == "product doesn't exist"


async def test_update_order_status(client, create_order_in_db,
                                   create_user_in_db):
    user_id = await create_user_in_db('test_username')
    order_id = await create_order_in_db(user_id)
    resp = client.patch(f'/orders/{order_id}/status',
                        data=json.dumps({'status': 'checkout'}))
    assert resp.status_code == 200
    resp = client.patch(f'/orders/{order_id}/status',
                        data=json.dumps({'status': 'invalid status'}))
    assert resp.status_code == 422
    assert resp.json()['detail'][0]['msg'] == "Input should be 'pending', \
'checkout', 'shipping', 'completed' or 'cancelled'"


async def test_delete_item_from_order(client, create_order_in_db,
                                 create_user_in_db, create_product_in_db,
                                 add_item_to_order, get_order_from_db):
    user_id = await create_user_in_db('test_username')
    order_id = await create_order_in_db(user_id)
    product_name = await create_product_in_db('test_product1', 150)
    product_name1 = await create_product_in_db('test_product2', 150)
    await add_item_to_order(order_id, product_name, 2)
    await add_item_to_order(order_id, product_name1, 3)
    resp = client.delete(f'/orders/{order_id}/item/{product_name}')
    assert resp.status_code == 200
    order = await get_order_from_db(order_id)
    assert len(order['content']) == 1
    assert order['content'][0]['product_name'] == 'test_product2'

    resp = client.delete(f'/orders/{order_id}/item/{product_name}')
    assert resp.status_code == 404
    assert resp.json()['detail'] == 'product is not in order'

    resp = client.delete(f'/orders/{order_id + 1}/item/{product_name1}')
    assert resp.status_code == 404
    assert resp.json()['detail'] == "order doesn't exist"

    resp = client.delete(f'/orders/{order_id}/item/not_existing_name')
    assert resp.status_code == 404
    assert resp.json()['detail'] == "product doesn't exist"
