from django.urls import path
from . import views

app_name = 'impact'

urlpatterns = [
    path('', views.impact_dashboard_view, name='dashboard'),
    path('challenges/<slug:challenge_slug>/report/new/', views.impact_report_create_view, name='report_create'),
    path('reports/<int:pk>/', views.impact_report_detail_view, name='report_detail'),
]
