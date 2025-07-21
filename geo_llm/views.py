from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, ListView, FormView
from geo_llm.models import Question
from geo_llm.forms import QuestionForm
from pathlib import Path
import sys
from geo_teacher_llm.agents.graph_orchestration_agent2 import app, GeoTeacherState
from django.urls import reverse_lazy

class QuestionView(LoginRequiredMixin, FormView):
    template_name="geo_llm/ask_question.html"
    login_url='/login'
    model = Question
    form_class = QuestionForm
    def form_valid(self, form):
        question = form.cleaned_data['question_text']
        response = app.invoke({"input": question})
        if isinstance(response, dict):
            answer = response.get("geo_teacher_answer", "No answer returned.")
        else:
            answer = str(response)

        self.answer = answer
        self.messages = response.get("messages", [])
        self.images = response.get("images", [])
        for image in self.images:
            print(image['url'])

        context = self.get_context_data(form=form, answer=answer, messages = self.messages, images = self.images)
        return self.render_to_response(context)