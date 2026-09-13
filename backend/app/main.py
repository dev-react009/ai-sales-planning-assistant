from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.sales_reps import router as sales_reps_router
from app.api.quota import router as quota_router
from app.api.accounts import router as accounts_router
from app.api.chat import router as chat_router

app = FastAPI(
    title="AI Sales Planning Assistant",
    description="An API for assisting with AI-driven sales planning.",
    version="1.0.0"
)
@app.get("/api/health") 
def health_check():   
    return {"status": "ok"}

app.include_router(sales_reps_router)
app.include_router(quota_router)
app.include_router(accounts_router)
app.include_router(chat_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)










