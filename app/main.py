from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.health import health_router
from app.routes.swap_action import swap_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "This is Sola AI swap service"}


# health route
app.include_router(health_router, prefix="/swap-api", tags=["Health"])
# swap route
app.include_router(swap_router, prefix="/swap-api", tags=["Swap"])
