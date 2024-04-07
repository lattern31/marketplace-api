import asyncio
from datetime import datetime
import os
from typing import Callable

from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import text

from api.app import create_app
from api.deps import get_async_session
from common.settings import settings
from models.users import UserRole


CLEAN_TABLES = [
    'users',
    'products',
    'orders',
    'orders_products',
]


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
def run_migrations():
    os.system('alembic -n test revision --autogenerate\
            -m "test running migration"')
    os.system('alembic -n test upgrade head')


async def _get_test_async_session():
    try:
        test_async_engine = create_async_engine(
            settings.db_test_string,
            echo=settings.debug,
        )
        session_maker = async_sessionmaker(
                test_async_engine, expire_on_commit=False)
        test_async_session = session_maker()
        yield test_async_session
    finally:
        await test_async_session.close()


@pytest.fixture(scope="function")
def app():
    app = create_app()
    app.dependency_overrides[get_async_session] = _get_test_async_session
    return app


@pytest.fixture(scope="function")
def client(app: FastAPI) -> TestClient:
    return TestClient(app)


@pytest.fixture(scope="session")
async def get_async_sessionmaker():
    engine = create_async_engine(settings.db_test_string, echo=settings.debug)
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    yield async_session


@pytest.fixture(scope="function", autouse=True)
async def clean_tables(get_async_sessionmaker):
    async with get_async_sessionmaker() as session:
        async with session.begin():
            for table_to_clean in CLEAN_TABLES:
                await session.execute(
                    text(f"truncate {table_to_clean} cascade"))


@pytest.fixture
async def get_product_from_db(get_async_sessionmaker):
    async def get_product_from_db_by_id(product_id: int):
        async with get_async_sessionmaker() as session:
            return (await session.execute(
                text("select * from products where id = :product_id"),
                {'product_id': product_id})
                ).all()[0]

    return get_product_from_db_by_id


@pytest.fixture
async def create_product_in_db(get_async_sessionmaker) -> int:
    async def create_product_in_db(title: str, cost: int, seller_id: int):
        async with get_async_sessionmaker() as session:
            async with session.begin():
                return (await session.execute(
                    text("""insert into products 
                    (title, cost, seller_id, created_at)
                    values (:title, :cost, :seller_id, :now)
                    returning products.id"""),
                    {"title": title,
                     'cost': cost,
                     'seller_id': seller_id,
                     'now': datetime.utcnow()})
                ).scalar()

    return create_product_in_db


@pytest.fixture
async def get_user_from_db(get_async_sessionmaker):
    async def get_user_from_db_by_id(user_id: int):
        async with get_async_sessionmaker() as session:
            return (await session.execute(
                text("select * from users where id = :user_id"),
                {'user_id': user_id})
            ).all()

    return get_user_from_db_by_id


@pytest.fixture
async def create_user_in_db(get_async_sessionmaker) -> int:
    async def create_user_in_db(username: str, role: UserRole):
        async with get_async_sessionmaker() as session:
            async with session.begin():
                return (await session.execute(
                    text("""insert into users (username, role, created_at)
                    values (:username, :role :now)
                    returning users.id"""),
                    {"username": username,
                     "role": role,
                     'now': datetime.utcnow()})
                ).scalar()

    return create_user_in_db


@pytest.fixture
async def get_cart_from_db(get_async_sessionmaker):
    async def get_cart_from_db(user_id: int):
        async with get_async_sessionmaker() as session:
            cart = await session.execute(
                text("select * from cart where user_id = :user_id"),
                {'user_id': user_id}
            )
            return [item._asdict() for item in cart.all()]

    return get_cart_from_db


@pytest.fixture
async def add_item_to_cart_in_db(get_async_sessionmaker):
    async def add_item_to_cart_in_db(
        user_id: int, product_id: int, quantity: int):
        async with get_async_sessionmaker() as session:
            async with session.begin():
                cart = await session.execute(
                    text("""insert into cart (user_id, product_id, quantity)
                         values(:user_id, :product_id, :quantity)"""),
                     {'user_id': user_id,
                      'product_id': product_id,
                      'quantity': quantity}
                )

    return add_item_to_cart_in_db


@pytest.fixture
async def get_order_from_db(get_async_sessionmaker):
    async def get_order_from_db_by_id(order_id: int):
        async with get_async_sessionmaker() as session:
            order = await session.execute(
                text("select * from orders where id = :order_id"),
                {'order_id': order_id}
            )
            order = order.one()._asdict()
            content = await session.execute(
                text("select * from orders_products\
                        where order_id = :order_id"),
                {'order_id': order_id})
            order['content'] = [product._asdict() for product in content.all()]
            return order
    return get_order_from_db_by_id


@pytest.fixture
async def create_order_in_db(get_async_sessionmaker) -> int:
    async def create_order_in_db(user_id: int, content: list['Product']):
        async with get_async_sessionmaker() as session:
            async with session.begin():
                order_id = (await session.execute(
                    text("""insert into orders (owner_id, status, created_at)
                    values (:owner_id, :status, :now)
                    returning orders.id"""),
                    {'owner_id': user_id,
                     'status': 'OPENED',
                     'now': datetime.utcnow()})
                ).scalar()
                await session.execute(
                    text("""insert into orders_products 
                    (order_id, product_id, quantity, status)
                    values (:order_id, :product_id, :quantity, :status)"""),
                    [{'order_id': order_id,
                      'product_id': item['id'],
                      'quantity': item['quantity'],
                      'status': 'PENDING'} for item in content]
                )
                return order_id

    return create_order_in_db


@pytest.fixture
async def create_test_user_and_get_token(
    app: FastAPI,
    client: TestClient,
) -> Callable:
    async def create_test_user_and_get_token(
        name: str,
        role: UserRole
    ) -> 'AuthHeader':
        reg_url = app.url_path_for('register_user')
        login_url = app.url_path_for('login_for_auth_token')
        resp = client.post(
            url=reg_url,
            json={
                'username': name,
                'role': role,
                'password': 'test'
            }
        )
        user_id = resp.json()['id']
        form_data = {
            'username': name,
            'password': 'test'
        }
        resp = client.post(
            url=login_url,
            data=form_data,
        )
        return (
            user_id, 
            {'Authorization': f'Bearer {resp.json()["access_token"]}'}
        )
    return create_test_user_and_get_token
