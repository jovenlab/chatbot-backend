from django.urls import path
from .views import hello, register_user, chatbot, get_conversation

urlpatterns = [
    path('hello/', hello),
    path('register/', register_user),
    path("chat/", chatbot, name="chatbot"),
    path('history/', get_conversation),
]
