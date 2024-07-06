"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from maas import views

#router = routers.DefaultRouter()
#router.register(r'maas', views.ContestView, 'contests')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/contests/<int:id>', views.ContestDetailView.as_view()),
    #path('api/team', views.TeamView.as_view()),
    #path('api/envs', views.EnvironmentView.as_view()),
    path('api/generate', views.GenerateView.as_view()),
    path('api/contestsinfo', views.ContestTableView.as_view()),
    path('create/contest', views.CreateContestView.as_view()),
    path('delete/contest', views.DeteleContestView.as_view()),
    path('reboot/contest', views.RebootContestView.as_view()),
    path('import/teams', views.ImportTeamsView.as_view()),
    path('api/conteststatus', views.ContestStatusView.as_view()),
    path('api/team/<int:id>', views.TeamDetailView.as_view()),
    path('create/environment', views.CreateEnvironmentView.as_view()),
    path('delete/environment', views.DeleteEnvironmentView.as_view()),  
    path('reboot/environment', views.RebootEnvironmentView.as_view()),  
    path('edit/contest', views.EditContestView.as_view()),  
    path('delete/team', views.DeleteTeamView.as_view())
]
