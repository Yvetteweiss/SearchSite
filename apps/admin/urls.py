from django.urls import path

from . import views

app_name = 'admin'

urlpatterns = [
    path('', views.index, name='index'),
    path('jobs/', views.jobs, name='jobs'),
    path('configurations/', views.configurations, name='configurations'),
    path('configurations/add/', views.AddConfigurationView.as_view(), name='configurations.add'),
    path('configurations/edit/', views.EditConfigurationView.as_view(), name='configurations.edit'),
    path('configurations/delete/', views.configurations_delete, name='configurations.delete'),
    path('configurations/detail/', views.configurations_detail, name='configurations.detail'),
]
