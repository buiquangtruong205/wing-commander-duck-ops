from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.ws_routes import router as ws_router
from app.core.config import settings

app = FastAPI(title=settings.APP_NAME)

# CORS Setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routes
app.include_router(ws_router)

@app.get("/")
async def root():
    return {"message": "Wing Commander Duck Ops API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
