from django.urls import path
from . import views

app_name = 'collaboration'

urlpatterns = [
    path('challenges/<slug:challenge_slug>/team/new/', views.team_create_view, name='team_create'),
    path('teams/<int:pk>/', views.team_detail_view, name='team_detail'),
    path('teams/<int:pk>/join/', views.team_join_request_view, name='team_join'),
    path('teams/<int:pk>/members/<int:membership_id>/<str:action>/', views.team_membership_action_view, name='membership_action'),
    path('teams/<int:pk>/tasks/new/', views.task_create_view, name='task_create'),
    path('teams/<int:pk>/tasks/<int:task_id>/status/', views.task_update_status_view, name='task_update_status'),
    path('teams/<int:pk>/tasks/<int:task_id>/delete/', views.task_delete_view, name='task_delete'),
    path('teams/<int:pk>/milestones/new/', views.milestone_create_view, name='milestone_create'),
    path('teams/<int:pk>/milestones/<int:milestone_id>/toggle/', views.milestone_toggle_view, name='milestone_toggle'),
]
