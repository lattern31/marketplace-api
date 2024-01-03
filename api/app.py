from fastapi import FastAPI
from api.handlers.orders import router as order_router
from api.handlers.products import router as product_router
from api.handlers.users import router as user_router


def create_app():
    app = FastAPI(
        title="Shopping cart API",
        docs_url='/api/docs',
    )

    app.include_router(order_router, prefix='/api/v1')
    app.include_router(product_router, prefix='/api/v1')
    app.include_router(user_router, prefix='/api/v1')

    return app

