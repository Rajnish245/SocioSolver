from django.urls import path
from . import views

app_name = 'solutions'

urlpatterns = [
    path('challenges/<slug:challenge_slug>/propose/', views.proposal_create_view, name='proposal_create'),
    path('proposals/<int:pk>/', views.proposal_detail_view, name='proposal_detail'),
    path('proposals/<int:pk>/edit/', views.proposal_update_view, name='proposal_update'),
    path('proposals/<int:pk>/delete/', views.proposal_delete_view, name='proposal_delete'),
    path('proposals/<int:pk>/vote/', views.toggle_vote_view, name='toggle_vote'),
    path('comments/add/', views.add_comment_view, name='add_comment'),
]
