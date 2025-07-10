from fastapi import FastAPI
from routes import predict, auth
from db.session import creation
# from models.user import User, Prediction
from fastapi.openapi.utils import get_openapi

app = FastAPI(title="fastapi")

app.include_router(predict.router, prefix="/predict", tags=["predict"])
# app.include_router(user.router, tags=["user"])
app.include_router(auth.router, tags=["auth"])

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="API simple",
        version="1.0.0",
        description="API avec Bearer Token simple",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "bearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        }
    }
    for path in openapi_schema["paths"].values():
        for method in path.values():
            method["security"] = [{"bearerAuth": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

creation()

