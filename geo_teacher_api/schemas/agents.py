from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class QuestionRequest(BaseModel):
    question: dict


class AnswerResponse(BaseModel):
    input: Optional[str] = None
    route: Optional[str] = None
    messages: Optional[List[str]] = []
    country: Optional[str] = None
    images: Optional[List[Dict[str, Any]]] = []
    capital_city: Optional[str] = None
    geo_teacher_answer: Optional[str] = None
    lat: Optional[float] = None
    lon: Optional[float] = None
    city: Optional[str] = None
    weather_info: Optional[str] = None
    fetched_places: Optional[List[Dict[str, Any]]] = []
    activity_suggestions: Optional[Dict[str, Any]] = {}