from django.urls import path
from .views import execute_query

urlpatterns = [
    #path('chatbot/', chatbot, name='chatbot')
     path('execute-query/', execute_query, name='execute_query'),
]
