import asyncio
from datetime import datetime
import os

from fastapi.testclient import TestClient
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import sessionmaker
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
    os.system('alembic -n test revision --autogenerate -m "test running migration"')
    os.system('alembic -n test upgrade head')

async def _get_test_async_session():
    try:
        test_async_engine: AsyncEngine = create_async_engine(
            settings.db_test_string,
            echo=settings.debug,
        )
        session_maker = async_sessionmaker(test_async_engine, expire_on_commit=False)
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
                await session.execute(text(f"truncate {table_to_clean} cascade"))

@pytest.fixture
async def get_product_from_db(get_async_sessionmaker):
    async def get_product_from_db_by_name(product_name: str):
        async with get_async_sessionmaker() as session:
            res = await session.execute(
                text(f"select * from products where name = :product_name"),
                {'product_name': product_name})
            return res.all()
    return get_product_from_db_by_name

@pytest.fixture
async def create_product_in_db(get_async_sessionmaker) -> str:
    async def create_product_in_db(product_name: str, cost: int):
        async with get_async_sessionmaker() as session:
            async with session.begin():
                return (await session.execute(text(f"""
                    insert into products (name, cost, created_at) 
                    values (:product_name, :cost, :now) 
                    returning products.name"""),
                    {"product_name": product_name, 
                     'cost': cost, 
                     'now': datetime.utcnow()})
                ).scalar()
    return create_product_in_db

@pytest.fixture
async def get_user_from_db(get_async_sessionmaker):
    async def get_user_from_db_by_id(user_id: int):
        async with get_async_sessionmaker() as session:
            res = await session.execute(
                text(f"select * from users where id = :user_id"),
                {'user_id': user_id})
            return res.all()
    return get_user_from_db_by_id

@pytest.fixture
async def create_user_in_db(get_async_sessionmaker) -> int:
    async def create_user_in_db(username: str):
        async with get_async_sessionmaker() as session:
            async with session.begin():
                return (await session.execute(text(
                    f"""insert into users (username, created_at) 
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
                text(f"select * from orders where id = :order_id"),
                {'order_id': order_id})
            order = order.one()._asdict()
            content = await session.execute(
                text(f"select * from orders_products where order_id = :order_id"),
                {'order_id': order_id})
            order['content'] = [product._asdict() for product in content.all()]
            return order
    return get_order_from_db_by_id

@pytest.fixture
async def create_order_in_db(get_async_sessionmaker) -> int:
    async def create_order_in_db(user_id: int):
        async with get_async_sessionmaker() as session:
            async with session.begin():
                return (await session.execute(text(f"""
                    insert into orders (user_id, status, created_at) 
                    values (:user_id, 'PENDING', :now) 
                    returning orders.id"""),
                    {'user_id': user_id, 
                     'now': datetime.utcnow()})
                ).scalar()
    return create_order_in_db
