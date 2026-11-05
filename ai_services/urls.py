from django.urls import path
from . import views

app_name = 'ai_services'

urlpatterns = [
    path('challenges/<int:challenge_id>/analyze/', views.analyze_challenge_view, name='analyze_challenge'),
    path('challenges/<int:challenge_id>/solutions/', views.generate_solutions_view, name='generate_solutions'),
    path('challenges/<int:challenge_id>/similar/', views.similar_challenges_view, name='similar_challenges'),
    path('challenges/<int:challenge_id>/team-matches/', views.smart_team_matching_view, name='team_matches'),
]
