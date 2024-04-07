from fastapi import FastAPI

from api.handlers.orders import router as order_router
from api.handlers.products import router as product_router
from api.handlers.users import router as user_router
from api.handlers.auth import router as auth_router
from api.handlers.cart import router as cart_router
from api.handlers.sellers import router as seller_router


def create_app():
    app = FastAPI(
        title="Shopping cart API",
        docs_url='/api/docs',
    )

    app.include_router(user_router, prefix='/api/me' )
    app.include_router(order_router, prefix='/api/me')
    app.include_router(auth_router, prefix='/api')
    app.include_router(cart_router, prefix='/api')
    app.include_router(product_router, prefix='/api')
    app.include_router(seller_router, prefix='/api')

    return app
