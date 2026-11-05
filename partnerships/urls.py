from django.urls import path
from . import views

app_name = 'partnerships'

urlpatterns = [
    path('organizations/', views.org_list_view, name='org_list'),
    path('organizations/<int:pk>/', views.org_detail_view, name='org_detail'),
    path('organizations/profile/manage/', views.org_profile_manage_view, name='org_manage'),
    path('challenges/<slug:challenge_slug>/partner/', views.partnership_request_create_view, name='partnership_request'),
    path('partnerships/<int:pk>/<str:action>/', views.partnership_action_view, name='partnership_action'),
    path('challenges/<slug:challenge_slug>/sponsor/', views.sponsored_challenge_create_view, name='sponsored_challenge_create'),
]
