from django.urls import path
from .views import CreateIssueView, GetIssueView

urlpatterns = [
    path('create_issue/', CreateIssueView.as_view(),
         name='create_issue'),  # Define the URL for TestTokenView
    # Define the URL for TestTokenView
    path('issues/', GetIssueView.as_view(), name='get_issue'),
]
