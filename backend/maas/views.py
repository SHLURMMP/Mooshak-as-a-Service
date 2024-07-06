import json
import boto3
import paramiko
import subprocess
import os
import base64
import struct
import string, random, datetime, copy
import ansible_runner
import sys

#from ldap3 import Server, Connection, ALL

from paramiko.util import deflate_long
from django.shortcuts import render
from django.http import JsonResponse
from rest_framework.views import APIView
from .serializers import *
from .models import *
from .forms import *

def get_attr(instance_name, attr):

    ec2 = boto3.client('ec2', region_name = 'eu-west-1')

    instance_data = ec2.describe_instances(
        Filters=[
            {
                'Name': 'tag:Name',
                'Values': [
                    instance_name,
                ],
            },
        ],
    )

    if attr == 'url':
        return instance_data['Reservations'][0]['Instances'][0]['PublicDnsName'] + '/~mooshak'
    elif attr == 'id':
        return instance_data['Reservations'][0]['Instances'][0]['InstanceId']
    elif attr == 'ip':
        return instance_data['Reservations'][0]['Instances'][0]['PublicIpAddress']

def create_keyfile(key_name):

    ec2 = boto3.client('ec2', region_name = 'eu-west-1')
    
    keypairResponse = ec2.create_key_pair(KeyName = key_name)

    with open('/home/pedro/MAAS/keyfiles/' + key_name +'.pem', 'w') as file:
        file.write(keypairResponse['KeyMaterial'])

    os.chdir('/home/pedro/MAAS/keyfiles')
    os.chmod(key_name + ".pem",0o600) 

    return keypairResponse['KeyMaterial']
    
def delete_environment(user_name):
    
    workspaces = boto3.client('workspaces', region_name = 'eu-west-1')

    env_info = workspaces.describe_workspaces(
        DirectoryId = 'd-936749afc9',
        UserName = user_name,
    )

    response = workspaces.terminate_workspaces(
        TerminateWorkspaceRequests=[
        {
            'WorkspaceId': env_info['Workspaces'][0]['WorkspaceId']
        },
        ]
    )

    return 0

def edit_keyfile(old_name, new_name):

    Contest.objects.filter(title = old_name).update(title = new_name)

    ec2 = boto3.client('ec2', region_name = 'eu-west-1')
    #response = ec2.describe_key_pairs(
    #    KeyNames = [
    #        'KeyPair' + old_name,
    #    ],
    #    IncludePublicKey = True
    #)

    #print(response['KeyPairs'][0]['PublicKey'])
    #public_key = 'ssh-rsa' + response['KeyPairs'][0]['PublicKey']
    #public_key_b = response['KeyPairs'][0]['PublicKey'].encode('utf-8')
    
    #VAI BUSCAR PUBLIC KEY
    key = paramiko.RSAKey.from_private_key_file('/home/pedro/MAAS/keyfiles/KeyPair' + old_name + '.pem')    

    output = b''
    parts = [b'ssh-rsa', deflate_long(key.public_numbers.e), deflate_long(key.public_numbers.n)]

    for part in parts:
        output += struct.pack('>I', len(part)) + part
    public_key = b'ssh-rsa ' + base64.b64encode(output) + b'\n' 

    response2 = ec2.import_key_pair(
        KeyName = 'KeyPair' + new_name,
        PublicKeyMaterial = public_key,
    )

    response = ec2.delete_key_pair(
            KeyName='KeyPair' + old_name,
        )

    #TROCA NOME DE FICHEIRO
    old_file = '/home/pedro/MAAS/keyfiles/KeyPair' + old_name + '.pem'
    new_file = '/home/pedro/MAAS/keyfiles/KeyPair' + new_name + '.pem'
    os.rename(old_file, new_file)
    return 0

def create_password():

    time = datetime.datetime.now().timestamp()
    #print(time)
    seedx = os.getpid() * time
    random.seed(seedx)
    password = ''

    while(any(punct in password for punct in string.punctuation) == False and any(digit in password for digit in string.digits) == False and any(let in password for let in string.ascii_letters) == False):

        password = ''.join([random.choice(string.ascii_letters + string.digits + string.punctuation ) for n in range(12)])
        print(password)

    return password

class ContestDetailView(APIView):

    def get(self, request, id):

        contest = Contest.objects.get(id = id)
        serializer = ContestDetailSerializer(contest)
        contest_data = serializer.data

        ec2 = boto3.client('ec2', region_name = 'eu-west-1')

        instance_data = ec2.describe_instances(
            Filters=[
                {
                    'Name': 'tag:Name',
                    'Values': [
                        contest_data['title'],
                    ],
                },
        ],
        )

        if instance_data['Reservations'][0]['Instances'][0]['State']['Name'] == 'running':
            
            contest_data['is_online'] = True
            new_url = instance_data['Reservations'][0]['Instances'][0]['PublicDnsName'] + '/~mooshak'
            contest_data['url'] = new_url

            Contest.objects.filter(id = contest_data['id']).update(is_online = True)
            Contest.objects.filter(id = contest_data['id']).update(url = new_url)

        else:
            contest_data['is_online'] = False
            new_url = instance_data['Reservations'][0]['Instances'][0]['PublicDnsName'] + '/~mooshak'
            contest_data['url'] = new_url

            Contest.objects.filter(id = contest_data['id']).update(is_online = False)
            Contest.objects.filter(id = contest_data['id']).update(url = new_url)

        #print(contest_data)

        workspaces = boto3.client('workspaces', region_name = 'eu-west-1')

        index = 0
        for team in contest_data['teams']:
            #print(contest_data['teams'][index])
            team_aux = Team.objects.get(id = team['id'])
            #print(team_aux)
            if team['has_env']:

                env_info = workspaces.describe_workspaces(
                    DirectoryId = 'd-936749afc9',
                    UserName = team['title'],
                )
                #print(env_info)

                if 'ComputerName' in env_info['Workspaces'][0]:
                    Team_Environment.objects.filter(team = team_aux).update(name = env_info['Workspaces'][0]['ComputerName'])
                    contest_data['teams'][index]['environment']['name'] = env_info['Workspaces'][0]['ComputerName']
                if 'IpAddress' in env_info['Workspaces'][0]:
                    Team_Environment.objects.filter(team = team_aux).update(ipv4_address = env_info['Workspaces'][0]['IpAddress'])
                    contest_data['teams'][index]['environment']['ipv4_address'] = env_info['Workspaces'][0]['IpAddress']
            
                if env_info['Workspaces'][0]['State'] == 'AVAILABLE':
                    Team_Environment.objects.filter(team = team_aux).update(is_online = True)
                    contest_data['teams'][index]['environment']['is_online'] = True
                else:
                    Team_Environment.objects.filter(team = team_aux).update(is_online = False)
                    contest_data['teams'][index]['environment']['is_online'] = False

            index += 1
        return JsonResponse({"contest":contest_data}, status = 200)    

class TeamDetailView(APIView):

    def get(self, request, id):

        team_aux = Team.objects.get(id = id)
        serializer = TeamsSerializer(team_aux)
        team_data = serializer.data

        workspaces = boto3.client('workspaces', region_name = 'eu-west-1')
        env_info = workspaces.describe_workspaces(
            DirectoryId = 'd-936749afc9',
            UserName = team_data['title'],
        )

        if team_data['environment'] != {}:
            if 'ComputerName' in env_info['Workspaces'][0]:
                Team_Environment.objects.filter(team = team_aux).update(name = env_info['Workspaces'][0]['ComputerName'])
                team_data['environment']['name'] = env_info['Workspaces'][0]['ComputerName']
            if 'IpAddress' in env_info['Workspaces'][0]:
                Team_Environment.objects.filter(team = team_aux).update(ipv4_address = env_info['Workspaces'][0]['IpAddress'])
                team_data['environment']['ipv4_address'] = env_info['Workspaces'][0]['IpAddress']
         
            if env_info['Workspaces'][0]['State'] == 'AVAILABLE':
                Team_Environment.objects.filter(team = team_aux).update(is_online = True)
                team_data['environment']['is_online'] = True
            else:
                Team_Environment.objects.filter(team = team_aux).update(is_online = False)
                team_data['environment']['is_online'] = False

        return JsonResponse({'team':team_data}, status = 200)

class CreateEnvironmentView(APIView):
    def post(self, request):
        
        teams_data = json.loads(request.body.decode('utf-8'))

        created_environments = 0

        for team in teams_data:
            team_aux = Team.objects.get(id = team['id'])
            team_info = TeamsSerializer(team_aux)
            team_info = team_info.data
            
            #print(team_info['environment'])
            if team_info['environment'] != {}:
                print('Environment Already Created')
                continue
            contest_aux = Contest.objects.get(id = team_info['contest'])
            contest_info = ContestSerializer(contest_aux)
            contest_info = contest_info.data

            environment = {}

            password = create_password()

            #CREATE USER IN DIRECTORY

            #server = Server('maas.clients.com', port = 389, get_info= ALL)
            #conn = Connection(server, user='teste',password='P3ixeC@rn3', auto_bind=True)
            #print('here2')

            #OVERRRRRRR
            
            workmail = boto3.client('workmail', region_name = 'eu-west-1')

            response = workmail.create_user(
                OrganizationId = 'm-7a32987cc3ba435a8acfc8d1e96d11fb',
                Name = team_info['title'],
                DisplayName = 'ambiente' + team_info['title'],
                Password = password,
                Role='USER',
                HiddenFromGlobalAddressList=True
            )

            workspaces = boto3.client('workspaces', region_name = 'eu-west-1')

            env_info = workspaces.create_workspaces(
                Workspaces=[
                    {
                        'DirectoryId': 'd-936749afc9',
                        'UserName': team_info['title'],
                        'BundleId': 'wsb-208l8k46h', #PERFORMANCE
                        'WorkspaceProperties': {
                           'RunningMode': 'AUTO_STOP',
                            'RunningModeAutoStopTimeoutInMinutes': 60,
                            'RootVolumeSizeGib': 80,
                            'UserVolumeSizeGib': 10,
                            },
                        'Tags': [
                        {
                            'Key': 'Contest',
                            'Value': contest_info['title']
                       },
               ],
                    }
                ]
            )

            environment['name'] = 'Pending'#env_info['PendingRequests'][0]['ComputerName']
            environment['ipv4_address'] = 'Pending'#env_info['PendingRequests'][0]['IpAddress']
            environment['is_online'] = False
            environment['team'] = team_aux
            environment['password'] = password
            
            #created_environments['created_envs'].append(environment)
            created_environments += 1
            Team_Environment.objects.create(**environment)
        
        print(created_environments)
        return JsonResponse({'created_envs':created_environments}, status = 200)
    
class DeleteTeamView(APIView):

    def delete(self, request):

        team_id = request.headers['team']

        aux = Team.objects.get(id = team_id) 
        team_info = TeamsSerializer(aux)
        team_info = team_info.data

        #print(team_info)

        aux = Contest.objects.get(id = team_info['contest'])
        contest = ContestSerializer(aux)
        contest = contest.data
        
        #DELETE ENVIRONMENT IF EXISTS

        if team_info['has_env']:

            #print('has_env')
            workmail = boto3.client('workmail', region_name = 'eu-west-1')

            user_info = workmail.list_users(
                OrganizationId = 'm-7a32987cc3ba435a8acfc8d1e96d11fb',
                Filters = {
                    'DisplayNamePrefix' : 'ambiente' + team_info['title']
                }
            )

            delete_environment(team_info['title'])

            user_deletion = workmail.delete_user(
                OrganizationId = 'm-7a32987cc3ba435a8acfc8d1e96d11fb',
                UserId = user_info['Users'][0]['Id']
            )
            
        #DELETE TEAM FROM MOOSHAK

        contest_ip = get_attr(contest['title'], 'ip')

        #RUN ANSIBLE PLAYBOOK
        var_file = json.dumps(team_info)

        out, err, rc = ansible_runner.run_command(
        executable_cmd='ansible-playbook',
        cmdline_args=['delete_team.yaml', '--user', 'ubuntu', '--inventory', contest_ip + ',', '--private-key', '~/MAAS/keyfiles/KeyPair' + contest['title'] + '.pem', '--extra-vars', var_file],
        input_fd = sys.stdin,
        output_fd = sys.stdout,
        error_fd = sys.stderr,
        host_cwd='/home/pedro/MAAS/backend/terraform_scripts/ansible'
        )
        #print(out)

        #DELETE TEAM FROM DB
        team = Team.objects.get(id = team_id)
        team.delete()

        return JsonResponse({'team': 'deleted'}, status = 200)

class DeleteEnvironmentView(APIView):
    
    def delete(self, request):

        team_id = request.headers['team']

        aux = Team.objects.get(id = team_id) 
        team_info = TeamSerializer(aux)
        team_info = team_info.data

        workmail = boto3.client('workmail', region_name = 'eu-west-1')

        user_info = workmail.list_users(
            OrganizationId = 'm-7a32987cc3ba435a8acfc8d1e96d11fb',
            Filters = {
                'DisplayNamePrefix' : 'ambiente' + team_info['title']
            }
        )

        delete_environment(team_info['title'])

        user_deletion = workmail.delete_user(
            OrganizationId = 'm-7a32987cc3ba435a8acfc8d1e96d11fb',
            UserId = user_info['Users'][0]['Id']
        )

        #contest = Contest.objects.get(id = request.headers['contest'])
        env = Team_Environment.objects.get(team_id = team_id)
        env.delete()

        return JsonResponse({'team_environment': 'deleted'}, status = 200)

class RebootEnvironmentView(APIView):

    def get(self, request):

        aux = Team.objects.get(id = request.headers['team'])

        serializer = TeamsSerializer(aux)
        team_info = serializer.data

        workspaces = boto3.client('workspaces', region_name = 'eu-west-1')

        env_data = workspaces.describe_workspaces(
            DirectoryId ='d-936749afc9',
            UserName = team_info['title'],
        )

        if team_info['environment']['is_online'] == True :
            
            workspaces.stop_workspaces(
                StopWorkspaceRequests=[
                    {
                        'WorkspaceId': env_data['Workspaces'][0]['WorkspaceId']
                    },
                ]
            )

            Team_Environment.objects.filter(team = team_info['id']).update(is_online = False)
            return JsonResponse({'status': 'offline'}, status = 200)

        else:
            
            workspaces.start_workspaces(
                StartWorkspaceRequests=[
                    {
                        'WorkspaceId': env_data['Workspaces'][0]['WorkspaceId']
                    },
                ]
            )

            Team_Environment.objects.filter(team = team_info['id']).update(is_online = True)
            return JsonResponse({'status': 'online'}, status = 200)
            
class ContestTableView(APIView):

    def get(self, request):

        contests = Contest.objects.all()
        serializer = ContestInfoSerializer(contests, many = True)
        
        ec2 = boto3.client('ec2', region_name = 'eu-west-1')

        contests_data = serializer.data
        #print(serializer.data)
        for contest in contests_data:
            index = contests_data.index(contest)
            instance_data = ec2.describe_instances(
                Filters=[
                    {
                        'Name': 'tag:Name',
                        'Values': [
                            contest['title'],
                        ],
                    },
            ],
            )
            if len(instance_data['Reservations']) == 0:
                continue

            if instance_data['Reservations'][0]['Instances'][0]['State']['Name'] == 'running':

                contests_data[index]['is_online'] = True
                new_url = instance_data['Reservations'][0]['Instances'][0]['PublicDnsName'] + '/~mooshak'
                contests_data[index]['url'] = new_url

                Contest.objects.filter(id = contests_data[index]['id']).update(is_online = True)
                Contest.objects.filter(id = contests_data[index]['id']).update(url = new_url)

            else:

                contests_data[index]['is_online'] = False
                new_url = instance_data['Reservations'][0]['Instances'][0]['PublicDnsName'] + '/~mooshak'
                contests_data[index]['url'] = new_url

                Contest.objects.filter(id = contests_data[index]['id']).update(is_online = False)
                Contest.objects.filter(id = contests_data[index]['id']).update(url = new_url)

            #print(contests_data)
        return JsonResponse({"contests":contests_data}, status = 200)

class DeteleContestView(APIView):

    def delete(self, request):

        contest = Contest.objects.get(id = request.headers['contest'])
       
        serializer = ContestDetailSerializer(contest)
        

        ec2 = boto3.client('ec2', region_name = 'eu-west-1')

        os.chdir('/home/pedro/MAAS/backend/terraform_scripts')
        os.system("terraform workspace select workspace_" + str(serializer.data['id']))
        os.system("terraform destroy -target=\"aws_instance.my_instance\" -auto-approve")
        os.system("terraform workspace select default")
        os.system("terraform workspace delete -force workspace_" + str(serializer.data['id']))

        ec2.delete_key_pair(
            KeyName='KeyPair' + serializer.data['title'],
        )

        os.remove('/home/pedro/MAAS/keyfiles/KeyPair'+ serializer.data['title'] + '.pem')
        
        #ADD DELETING ALL TEAM ENVIRONMENTS 

        workmail = boto3.client('workmail', region_name = 'eu-west-1')

        teams = serializer.data['teams']

        for team in teams:
            
            if team['environment']:

                delete_environment(team['title'])

                workmail = boto3.client('workmail', region_name = 'eu-west-1')

                user_info = workmail.list_users(
                    OrganizationId = 'm-7a32987cc3ba435a8acfc8d1e96d11fb',
                    Filters = {
                        'DisplayNamePrefix' : 'ambiente' + team['title']
                    }
                )

                user_deletion = workmail.delete_user(
                    OrganizationId = 'm-7a32987cc3ba435a8acfc8d1e96d11fb',
                    UserId = user_info['Users'][0]['Id']
                )
            
        contest.delete()

        return JsonResponse({"deleted contest":"teste"}, status = 200)

class CreateContestView(APIView):

    def post(self, request):
        
        ec2 = boto3.client('ec2', region_name = 'eu-west-1')

        contest = json.loads(request.body.decode('utf-8'))
        full_contest = copy.deepcopy(contest)
        #print(full_contest)
        teams = contest.pop('teams')

        #CREATE CONTEST IN DATABASE
        Contest.objects.create(**contest)

        #CREATE TEAMS IN DATABASE
        for team in teams:
            team['contest'] = Contest.objects.get(title = contest['title'])
            #team.pop('group')
            Team.objects.create(**team)


        aux = Contest.objects.get(title = contest['title'])
        serializer = ContestDetailSerializer(aux)
        contest_id = serializer.data['id']

        #SETUP KEYPAIR
        key_name = 'KeyPair' + contest['title']
        create_keyfile(key_name)

        #RUN TERRAFORM SCRIPT
        #out = subprocess.run(["terraform","workspace","new", "workspace_" + str(contest_id)], capture_output= True, cwd='/home/pedro/MAAS/backend/terraform_scripts')
        os.chdir('/home/pedro/MAAS/backend/terraform_scripts')
        out = os.system("terraform workspace new workspace_" + str(contest_id))
        out = os.system("terraform apply -var='KeyPair=" + key_name + "' -var='ContestTitle=" + contest['title'] + "' -var='ContestDescription=" + contest['description'] + "' -var='ContestInstanceType=" + contest['contest_specs'] + "' -input=false -auto-approve")


        print('waiting until online')

        waiter = ec2.get_waiter('instance_status_ok')
        waiter.wait(
        InstanceIds = [ get_attr(contest['title'], 'id') ],
        Filters = [
            {
                "Name": "instance-status.reachability",
                "Values": [
                    "passed"
                ]
            }
            ]
        )

        #CREATE ANSIBLE VARS FILE
        contest_ip = get_attr(contest['title'], 'ip')

        print(full_contest)
        

        #EDIT ANSIBLE HOSTS FILE
        contest_ip = get_attr(contest['title'], 'ip')

        var_file = json.dumps(full_contest)

        out, err, rc = ansible_runner.run_command(
        executable_cmd='ansible-playbook',
        cmdline_args=['playbook.yaml', '--user', 'ubuntu', '--inventory', contest_ip + ',', '--private-key', '~/MAAS/keyfiles/KeyPair' + contest['title'] + '.pem', '--extra-vars', var_file],
        input_fd = sys.stdin,
        output_fd = sys.stdout,
        error_fd = sys.stderr,
        host_cwd='/home/pedro/MAAS/backend/terraform_scripts/ansible'
        )
        print(out)

        return JsonResponse({'contest': 'created'}, status = 200)
  
class EditContestView(APIView):
    
    def put(self, request):

        aux = Contest.objects.get(id = request.headers['contest'])
        
        serializer = ContestDetailSerializer(aux)
        contest = serializer.data

        new_contest = json.loads(request.body.decode('utf-8'))
        ec2 = boto3.client('ec2', region_name = 'eu-west-1')


        #RUN TERRAFORM SCRIPT
        #key_name = 'KeyPair' + new_contest['name']

        #out = subprocess.run(["terraform","workspace","select", "workspace_" + str(contest['id'])], capture_output= True, cwd='/home/pedro/MAAS/backend/terraform_scripts')
        #os.chdir('/home/pedro/MAAS/backend/terraform_scripts')
        #out = os.system("terraform apply -var='KeyPair=" + key_name + "' -var='ContestName=" + new_contest['name'] + "' -var='ContestDescription=" + new_contest['description'] + "' -var='ContestInstanceType=" + new_contest['contest_specs'] + "' -input=false -auto-approve")

        instance_id = get_attr(contest['title'], 'id')

        if new_contest['contest_specs'] != contest['contest_specs']:
            response = ec2.modify_instance_attribute(
                InstanceId = instance_id,
                Attribute = 'instanceType',
                InstanceType={
                    'Value': new_contest['contest_specs']
                },
            )
            
            Contest.objects.filter(title = contest['title']).update(contest_specs = new_contest['contest_specs'])

        if new_contest['description'] != contest['description']:
            response = ec2.delete_tags(
                Resources=[instance_id],
                Tags=[
                    {
                        'Key': 'Name',
                        'Value': contest['title'],
                    },
                ],
            )

            response = ec2.create_tags(
                Resources=[instance_id],
                Tags=[
                    {
                        'Key': 'Name',
                        'Value': new_contest['title'],
                    },
                ],
            )

            Contest.objects.filter(title = contest['title']).update(description = new_contest['description'])
        
        if new_contest['title'] != contest['title']:
            response = ec2.delete_tags(
                Resources=[instance_id],
                Tags=[
                    {
                        'Key': 'Name',
                        'Value': contest['title'],
                    },
                ],
            )

            response = ec2.create_tags(
                Resources=[instance_id],
                Tags=[
                    {
                        'Key': 'Name',
                        'Value': new_contest['title'],
                    },
                ],
            )

            edit_keyfile(contest['title'], new_contest['title'])
            Contest.objects.filter(title = contest['title']).update(title = new_contest['title'])
        
        print('waiting until online')

        waiter = ec2.get_waiter('instance_status_ok')
        waiter.wait(
        InstanceIds = [get_attr(new_contest['title'], 'id')],
        Filters = [
            {
                "Name": "instance-status.reachability",
                "Values": [
                    "passed"
                ]
            }
            ]
        )


        #EDIT ANSIBLE CONFIG

        contest_ip = get_attr(new_contest['title'], 'ip')

        var_file = json.dumps(new_contest)

        out, err, rc = ansible_runner.run_command(
        executable_cmd='ansible-playbook',
        cmdline_args=['edit_contest.yaml', '--user', 'ubuntu', '--inventory', contest_ip + ',', '--private-key', '~/MAAS/keyfiles/KeyPair' + new_contest['title'] + '.pem', '--extra-vars', var_file],
        input_fd = sys.stdin,
        output_fd = sys.stdout,
        error_fd = sys.stderr,
        host_cwd='/home/pedro/MAAS/backend/terraform_scripts/ansible'
        )
        print(out)

        #GET INSTANCE DATA
        data = ec2.describe_instances(
            InstanceIds=[
                get_attr(new_contest['title'], 'id'),
            ],
        )
        instance_data = data['Reservations'][0]['Instances'][0]

        new_contest['url'] = instance_data['PublicDnsName'] + '/~mooshak'

        if instance_data['State']['Name'] == 'running':
            new_contest['is_online'] = True
        else:
            new_contest['is_online'] = False
        
        
        Contest.objects.filter(title = contest['title']).update(is_online = new_contest['is_online'])
        Contest.objects.filter(title = contest['title']).update(url = new_contest['url'])

        return JsonResponse({'contest': 'edited'}, status = 200)

class RebootContestView(APIView):

    def get(self, request):

        aux = Contest.objects.get(id = request.headers['contest'])
        
        serializer = ContestDetailSerializer(aux)
        contest = serializer.data

        ec2 = boto3.client('ec2', region_name = 'eu-west-1')

        instance_id = get_attr(contest['title'], 'id')

        if contest['is_online'] == True:

            #print('here')
            ec2.stop_instances(
                InstanceIds=[
                    instance_id,
                ],
            )

            Contest.objects.filter(id = contest['id']).update(url = get_attr(contest['title'], 'url'))
            Contest.objects.filter(id = contest['id']).update(is_online = False)
            return JsonResponse({'status': 'offline'}, status = 200)

        else:

            #print('here')
            ec2.start_instances(
                InstanceIds=[
                    instance_id,
                ],
            )

            Contest.objects.filter(id = contest['id']).update(url = get_attr(contest['title'], 'url'))
            Contest.objects.filter(id = contest['id']).update(is_online = True)

            return JsonResponse({'status': 'online'}, status = 200)
   
class ImportTeamsView(APIView):

    def get(self, request):

        aux = Contest.objects.get(id = request.headers['contest'])

        serializer = ContestDetailSerializer(aux)
        contest = serializer.data

        #ec2 = boto3.client('ec2', region_name = 'eu-west-1')

        contest_ip = get_attr(contest['title'], 'ip')
        
        
        private_key = paramiko.RSAKey.from_private_key_file('/home/pedro/MAAS/keyfiles/KeyPair' + contest['title'] + '.pem')

        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        ssh.connect(hostname = contest_ip, username='ubuntu', pkey = private_key)

        commands = """
        cd ..;
        sudo find /home/mooshak/data/ -type d -exec chmod 755 {} \;
        sudo find /home/mooshak/data/ -type f -exec chmod 755 {} \;
        cd /home/mooshak/data/contests/contest_template/groups;
        ls -d */;
        """

        stdin, stdout, stderr = ssh.exec_command(commands)

        if stderr == '':
            return JsonResponse({'teams':'import failed'}, status = 500)

        aux = stdout.read().decode("utf-8").replace('/','')
        group_list = aux.split('\n')
        group_list.pop()

        for group in group_list:
            commands = "cd ..;cd /home/mooshak/data/contests/contest_template/groups/" + group + ";ls -d */;"
            
            stdin, stdout, stderr = ssh.exec_command(commands)

            
            if stderr == '':
                return JsonResponse({'teams':'import failed'}, status = 500)

            aux = stdout.read().decode("utf-8").replace('/','')
            team_list = aux.split('\n')
            team_list.pop()

            for team in team_list:
                
                team_info = {}

                commands = "cd ..;cd /home/mooshak/data/contests/contest_template/groups/"+ group +"/" + team + ";cat .data.tcl;"
                commands.replace
                stdin, stdout, stderr = ssh.exec_command(commands)

                if stderr == '':
                    return JsonResponse({'teams':'import failed'}, status = 500)

                team_lines = stdout.read().decode("utf-8").split('\n')

                for line in team_lines:               
                    
                    if 'Name' in line:
                        line = line.replace('set','')
                        line = line.replace(' ','')
                        line = line.replace('Name','')
                        team_info['title'] = line
                    if 'Email' in line:
                        line = line.replace('set','')
                        line = line.replace(' ','')
                        line = line.replace('Email','')
                        team_info['email'] = line
                
                team_info['group'] = group
                team_info['contest'] = Contest.objects.get(id = contest['id'])
                print(team_info)
                Team.objects.create(**team_info)

        
        ssh.close()

        return JsonResponse({'teams':'imported'}, status = 200)
    
class ContestStatusView(APIView):

    def get(self, request):
        
        aux = Contest.objects.get(id = request.headers['contest'])

        serializer = ContestDetailSerializer(aux)
        contest = serializer.data

        ec2 = boto3.client('ec2', region_name = 'eu-west-1')

        instance_id = get_attr(contest['title'], 'id')

        response = ec2.describe_instance_status(
            InstanceIds=[
                instance_id,
            ],
        )
        
        instance_status = {
            'contest' : contest['title'],
            'InstanceStatus' : response['InstanceStatuses'][0]['InstanceStatus'],
            'SystemStatus' : response['InstanceStatuses'][0]['SystemStatus']
        }


        return JsonResponse(instance_status, status = 200)

class GenerateView(APIView):

    def post(self, request):

        contest_list = [
            {'title': 'Teste', 'description': 'Concurso de Teste', 'url': 'google.com', 'is_online': 'True', 'config_file': 'Este é um ficheiro de teste'}
        ]

        Contest.objects.all().delete()

        for contest in contest_list:
            Contest.objects.create(**contest)

        team_list = [
            {'name': 'Equipa1', 'contest': Contest.objects.get(id = 1)},
            {'name': 'Equipa2', 'contest': Contest.objects.get(id = 1)}
        ]

        Team.objects.all().delete()

        for team in team_list:
            Team.objects.create(**team)

        Team_Environment.objects.all().delete()

        team_environment = [
            {
                'team' : Team.objects.get(id = 1), 'name': 'Ambiente Equipa 1', 'url' : 'ambiente.com', 'is_online': 'False'
            }
        ]
        for env in team_environment:
            Team_Environment.objects.create(**env)

        return JsonResponse({'created':'contests'}, status = 200)

#class TeamView(APIView):
#
#    def get(self, request):
#
#        teams = Team.objects.all()
#        serializer = TeamSerializer(teams, many = True)
#
#        return JsonResponse({"teams":serializer.data}, status = 200)