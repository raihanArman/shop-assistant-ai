from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routes import chat, products

app=FastAPI(title='Shop Assistant AI')

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router)
app.include_router(products.router)