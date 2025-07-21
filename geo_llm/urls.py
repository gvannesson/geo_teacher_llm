from django.urls import path
from .views import QuestionView

urlpatterns = [
    path('Question/', QuestionView.as_view(), name='ask_question'),
]