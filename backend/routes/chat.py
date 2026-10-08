from fastapi import APIRouter
from pydantic import BaseModel
from backend.services.gemini_chain import gen_response

router=APIRouter()

class ChatRequest(BaseModel):
    query:str
    history:list[str]=[]


@router.post("/chat")
def chat(request:ChatRequest):
    response,history=gen_response(request.query,request.history)
    return {"response":response,"history":history}
    