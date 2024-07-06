from rest_framework import serializers
from .models import *

class ContestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contest
        fields = ['id', 'title', 'description', 'url', 'is_online', 'contest_specs']

class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ['id', 'title', 'email', 'group', 'contest']

class TeamEnvironmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team_Environment
        fields = ['name', 'ipv4_address', 'is_online', 'password', 'team']

class TeamsSerializer(serializers.ModelSerializer):
    environment = serializers.SerializerMethodField()
    has_env = serializers.SerializerMethodField()

    class Meta:
        model = Team
        fields = ['id', 'title', 'email', 'group', 'mooshak_password', 'has_env', 'environment', 'contest']
    
    def get_environment(self, obj):
        
        if not Team_Environment.objects.filter(team = obj.id).exists():
            return {}
        
        env = Team_Environment.objects.get(team = obj.id)
        serializer = TeamEnvironmentSerializer(env)
        return serializer.data
    
    def get_has_env(self, obj):
        if not Team_Environment.objects.filter(team = obj.id).exists():
            return False
        else:
            return True

class ContestInfoSerializer(serializers.ModelSerializer):
    number_teams = serializers.SerializerMethodField()
    
    class Meta:
        model = Contest
        fields = ['id', 'title', 'description', 'url', 'is_online', 'number_teams']

    def get_number_teams(self, obj):

        return obj.teams.count()

class ContestDetailSerializer(serializers.ModelSerializer):
    teams = serializers.SerializerMethodField()
    
    class Meta:
        model = Contest
        fields = ['id', 'title', 'description', 'url', 'is_online', 'contest_specs', 'teams']

    def get_teams(self, obj):
        
        contest_teams = obj.teams
        serializer = TeamsSerializer(contest_teams, many = True)

        obj.teams
        return serializer.data
    
class TeamDetailSerializer(serializers.ModelSerializer):
    environment = serializers.SerializerMethodField()

    class Meta:
        model = Team
        fields = ['id', 'title', 'email', 'environment']

    def get_environment(self, obj):
        
        if not Team_Environment.objects.filter(team = obj.id).exists():
            return {}
        
        env = Team_Environment.objects.get(team = obj.id)
        serializer = TeamEnvironmentSerializer(env)
        return serializer.data