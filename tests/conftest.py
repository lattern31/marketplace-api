import asyncio
from datetime import datetime
import os

from fastapi.testclient import TestClient
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import text

from api.app import create_app
from api.deps import get_async_session
from common.settings import settings


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
def client():
    app = create_app()
    app.dependency_overrides[get_async_session] = _get_test_async_session
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
                ).all()
    return get_product_from_db_by_id


@pytest.fixture
async def create_product_in_db(get_async_sessionmaker) -> int:
    async def create_product_in_db(title: str, cost: int):
        async with get_async_sessionmaker() as session:
            async with session.begin():
                return (await session.execute(
                    text("""insert into products (title, cost, created_at)
                    values (:title, :cost, :now)
                    returning products.id"""),
                    {"title": title,
                     'cost': cost,
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
    async def create_user_in_db(username: str):
        async with get_async_sessionmaker() as session:
            async with session.begin():
                return (await session.execute(
                    text("""insert into users (username, created_at)
                    values (:username, :now)
                    returning users.id"""),
                    {"username": username,
                     'now': datetime.utcnow()})
                ).scalar()
    return create_user_in_db


@pytest.fixture
async def get_order_from_db(get_async_sessionmaker):
    async def get_order_from_db_by_id(order_id: int):
        async with get_async_sessionmaker() as session:
            order = await session.execute(
                text("select * from orders where id = :order_id"),
                {'order_id': order_id})
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
    async def create_order_in_db(user_id: int):
        async with get_async_sessionmaker() as session:
            async with session.begin():
                return (await session.execute(
                    text("""insert into orders (owner_id, status, created_at)
                    values (:owner_id, 'PENDING', :now)
                    returning orders.id"""),
                    {'owner_id': user_id,
                     'now': datetime.utcnow()})
                ).scalar()
    return create_order_in_db


@pytest.fixture
async def add_item_to_order(get_async_sessionmaker) -> int:
    async def add_item_to_order(order_id: int, product_id: int,
                                quantity: int):
        async with get_async_sessionmaker() as session:
            async with session.begin():
                await session.execute(
                    text("""insert into orders_products
                    (order_id, product_id, quantity)
                    values (:order_id, :product_id, :quantity)"""),
                    {'order_id': order_id,
                     'product_id': product_id,
                     'quantity': quantity})
    return add_item_to_order
