from django.db import models

# Create your models here.

class Contest(models.Model):
    id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length = 255, null=True)
    description = models.TextField(max_length = 512, null=True)
    url = models.CharField(max_length = 255, null=True)
    is_online = models.BooleanField(default = False)
    private_key = models.CharField(max_length = 255, null=True)
    contest_specs = models.CharField(max_length = 255, null=True)
    admin_password = models.CharField(max_length = 255, null=True)
    judge_password = models.CharField(max_length = 255, null=True)

class Team(models.Model):
    id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length = 255)
    email = models.CharField(max_length = 255, null=True)
    group = models.CharField(max_length = 255, null=True)
    contest = models.ForeignKey('Contest', on_delete = models.CASCADE, related_name = 'teams')
    mooshak_password = models.CharField(max_length = 255, null=True)

class Team_Environment(models.Model):
    team = models.OneToOneField(Team, on_delete = models.CASCADE, primary_key = True, related_name = 'environment')
    name = models.CharField(max_length = 255, null = True)
    password = models.CharField(max_length = 255, null = True)
    ipv4_address = models.CharField(max_length = 255, null = True)
    is_online = models.BooleanField(default = False)

