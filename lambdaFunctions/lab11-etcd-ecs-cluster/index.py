import json
import boto3
import os
import sys

session = boto3.session.Session()
ecsClient = session.client(service_name='ecs')
ec2Client = session.client(service_name='ec2')

route53Client = boto3.client('route53')

def pp(obj):
    #  pprint(obj, indent=3)
     print(json.dumps(obj, sort_keys=True,indent=3, separators=(',', ': ')))

def getHostPort(resp, taskArn, containerArn):
    hostPort = None
    if 'tasks' not in resp or len(resp["tasks"])<1:
        return None
    print("descTask resp=", resp["tasks"])
    for c in resp["tasks"][0]["containers"]:
        if c["containerArn"] == containerArn and c["taskArn"] == taskArn:
            if "networkBindings" not in c:
                continue
            hostPort = c["networkBindings"][0]["hostPort"]
            print("hostPort=%s" % hostPort)
    return hostPort


def descTask(clusterArn, taskArn, containerArn):
    resp = ecsClient.describe_tasks(
        cluster = clusterArn,
        tasks = [ taskArn ]
    )
    return resp


def getEc2InstancePrivateIp(containerArn, clusterArn):
    resp = ecsClient.describe_container_instances(
        cluster=clusterArn,
        containerInstances=[ containerArn ]
    )
    ec2InstanceId = resp["containerInstances"][0]["ec2InstanceId"]
    print("ec2InstanceId=%s" % ec2InstanceId)
    resp = ec2Client.describe_instances(
        InstanceIds=[ec2InstanceId]
    )
    if 'Reservations' not in resp or len(resp['Reservations'])<1:
        print('empty resp from describe_instances')
        return None
    for i in resp['Reservations'][0]['Instances']:
        if len(i['NetworkInterfaces'])>0:
            return i['NetworkInterfaces'][0]['PrivateIpAddress']
    return None
        
def update_route53(rraction, rrname, rrtype, rrvalueSet, rrttl=60):
    resp = route53Client.change_resource_record_sets(
        HostedZoneId=os.environ['R53ZoneId'],
        ChangeBatch={
            'Comment': '%s for %s' % (rrtype, rrname),
            'Changes': [
                {
                    'Action': rraction,
                    'ResourceRecordSet': {
                        'Name': rrname,
                        'Type': rrtype,
                        'TTL': rrttl,
                        'ResourceRecords': rrvalueSet
                    }
                }
            ]
        }
    )
    print(resp)

def generate_srv_rr(clusterArn):
    ip=[]
    resp = ecsClient.list_tasks(
        cluster=clusterArn
    )   
    if len(resp['taskArns'])==0:
        print('empty taskArns wtih list_tasks')
        return None
    #print(resp)
    resp = ecsClient.describe_tasks(
        cluster=clusterArn,
        tasks=resp['taskArns']
    ) 
    print(resp)
    if len(resp['tasks'])==0:
        print('empty tasks')
        return None
    for t in resp['tasks']:
        instancePrivateIp = getEc2InstancePrivateIp(t["containerInstanceArn"], clusterArn)
        print(instancePrivateIp)
        for c in t['containers']:
            if c['taskArn']==t['taskArn'] and t['desiredStatus']=='RUNNING':
                containerName = c['name']
                if 'networkBindings' not in c:
                    hostPort = None
                    continue
                for nb in c['networkBindings']:
                    if nb['containerPort']==2380:
                        hostPort = nb['hostPort']
                        break
                    else:
                        hostPort = None
        
    
        if containerName and instancePrivateIp and hostPort:
            ip.append( (containerName, instancePrivateIp, hostPort) )
    print(ip)
    return ip


def lambda_handler(event, context):    
    if event["detail-type"] != "ECS Task State Change":
        print("ignoring event: %s" % event["detail-type"])
        return "DONE"
    #print(pp(event))
    desiredStatus = event["detail"]["desiredStatus"]
    print("desiredStatus=%s" % desiredStatus)
    clusterArn = event["detail"]["clusterArn"]

    containerArn = event["detail"]["containers"][0]["containerArn"]
    taskArn = event["detail"]["taskArn"]
    containerInstanceArn = event["detail"]["containerInstanceArn"]
    desc = descTask(clusterArn, taskArn, containerArn)
    hostPort = getHostPort(desc, taskArn, containerArn)
    containerName = desc['tasks'][0]['containers'][0]['name']
    instancePrivateIp = getEc2InstancePrivateIp(containerInstanceArn, clusterArn)
    if not instancePrivateIp or not hostPort:
        print('ERROR - instance not found or hostPort not found')
        return 'false'
    print(instancePrivateIp, hostPort, containerName)
    if desiredStatus=="RUNNING":
        rraction="UPSERT"
    else:
        rraction="DELETE"
    try:
        update_route53(rraction, '%s.%s' % (containerName, os.environ['R53ZoneName']), 'A', [ { 'Value': instancePrivateIp }])
    except:
        print("Unexpected error:", sys.exc_info()[0])
    info = generate_srv_rr(clusterArn)
    if not info:
        return 'failed'
    # return [('etcd-node2', '10.0.2.127', 32769), ('etcd-node3', '10.0.2.245', 32771), ('etcd-node1', '10.0.2.245', 32769)]
    srv_info_server = []
    srv_info_client = []
    for i in range(len(info)):
        # print({
        #     'Value': '%s %s %s %s.%s' % (i+1, 10*(i+1), info[i][2], info[i][0], os.environ['R53ZoneName'])
        # })
        # srv_info.append({
        #     'Value': '%s %s %s %s.%s' % (i+1, 10*(i+1), info[i][2], info[i][0], os.environ['R53ZoneName'])
        # })
        print({
            'Value': '%s %s %s %s.%s' % (i+1, 10*(i+1), 2380, info[i][0], os.environ['R53ZoneName'])
        })
        srv_info_server.append({
            'Value': '%s %s %s %s.%s' % (i+1, 10*(i+1), 2380, info[i][0], os.environ['R53ZoneName'])
        })
        srv_info_client.append({
            'Value': '%s %s %s %s.%s' % (i+1, 10*(i+1), 2379, info[i][0], os.environ['R53ZoneName'])
        })
    if len(srv_info)>0:
        try:
            update_route53(rraction, '_etcd-server._tcp.%s' % os.environ['R53ZoneName'], 'SRV', srv_info_server)
            update_route53(rraction, '_etcd-client._tcp.%s' % os.environ['R53ZoneName'], 'SRV', srv_info_client)
        except:
            print("Unexpected error:", sys.exc_info()[0])
    return "OK"




