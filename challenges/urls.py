from django.urls import path
from . import views

app_name = 'challenges'

urlpatterns = [
    path('', views.landing_page_view, name='landing'),
    path('challenges/', views.challenge_list_view, name='challenge_list'),
    path('challenges/create/', views.challenge_create_view, name='challenge_create'),
    path('challenges/<slug:slug>/', views.challenge_detail_view, name='challenge_detail'),
    path('challenges/<slug:slug>/edit/', views.challenge_update_view, name='challenge_update'),
    path('challenges/<slug:slug>/delete/', views.challenge_delete_view, name='challenge_delete'),
    path('challenges/<slug:slug>/report/', views.challenge_report_view, name='challenge_report'),
    path('challenges/<slug:slug>/bookmark/', views.toggle_bookmark_view, name='toggle_bookmark'),
]
