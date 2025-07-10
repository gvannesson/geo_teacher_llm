from fastapi import APIRouter, Depends
from pydantic import BaseModel
from transformers import AutoTokenizer , AutoModelForSequenceClassification
import torch
from models.user import Prediction, User
from sqlmodel import create_engine, Session
from utils.jwt_handler import get_user
from pathlib import Path
from sqlmodel import create_engine

BASE_DIR = Path(__file__).resolve().parent.parent  # ← remonte jusqu'au dossier fastapi/
db_path = BASE_DIR / "db.sqlite3"

DATABASE_URL = f"sqlite:///{db_path}"

engine = create_engine(DATABASE_URL, echo=True)

engine = create_engine(DATABASE_URL, echo=True)

router = APIRouter()

tokenizer = AutoTokenizer.from_pretrained("book_genre_model")
model = AutoModelForSequenceClassification.from_pretrained("book_genre_model")

genre = {
    0 : 'crime',
    1 : 'fantasy',
    2 : 'history',
    3 : 'horror',
    4 : 'psychology',
    5 : 'romance',
    6 : 'science',
    7 : 'sports',
    8 : 'thriller',
    9 : 'travel'
}

class Item(BaseModel):
    text : str

def tokenisation(input) :
    output = tokenizer(input, return_tensors="pt") 
    return output

def modelisation(output):
    final = model(**output)
    logits = final.logits
    result = torch.argmax(logits, dim=1)
    return result.item()

@router.post("/")
async def predict(item: Item, current_user: User = Depends(get_user)):

    input = item.text
    encoded_input = tokenisation(input)
    modelisation_done = modelisation(encoded_input)
    result = genre[modelisation_done]
    create_prediction(current_user.id,input, result)
    print(current_user.id)
    return {"genre": result}

def create_prediction(user_id, input, result):
    pred1 = Prediction(user_id = user_id, summary=input,predicted_genre=result)

    with Session(engine) as session :
        session.add(pred1)
        session.commit()

