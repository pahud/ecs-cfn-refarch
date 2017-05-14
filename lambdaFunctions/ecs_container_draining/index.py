import sys
import json
import boto3
import time
# from pprint import pprint


session = boto3.session.Session()
stsClient = session.client(service_name='sts')
ec2Client = session.client(service_name='ec2')
asgClient = session.client('autoscaling')
ecsClient = session.client(service_name='ecs')
lambdaClient = session.client(service_name='lambda')

ec2InstanceId="i-04615c1698634242f"

def pp(obj):
    #  pprint(obj, indent=3)
     print(json.dumps(obj, sort_keys=True,indent=3, separators=(',', ': ')))

def getClusterName(ec2InstanceId=ec2InstanceId):
    resp =ec2Client.describe_tags(Filters=[
				{
					'Name': "resource-id", 
					'Values': [ ec2InstanceId ]
				},
				{
					'Name': "key", 
					'Values': ["ECS_CLUSTER"]
				} 
    ])
    # json_print(resp)
    for t in resp["Tags"]:
        if t["Key"]=="ECS_CLUSTER":
            return t["Value"]
    return None


def getContainerInstances(clusterName):
    resp = ecsClient.list_container_instances(
        cluster=clusterName
        # filter='string',
        # nextToken='string',
        # maxResults=123,
        # status='ACTIVE'|'DRAINING'
    )
    return resp["containerInstanceArns"]

def getContainerInstanceId(clusterName, containerInstanceArns,ec2InstanceId=ec2InstanceId):
    resp = ecsClient.describe_container_instances(
        cluster=clusterName,
        containerInstances=containerInstanceArns
    )
    # print(resp)
    for i in resp["containerInstances"]:
        if i["ec2InstanceId"]==ec2InstanceId:
            containerInstanceArn = i["containerInstanceArn"]
            status = i["status"]
            runningTasksCount = i["runningTasksCount"]
            return [ containerInstanceArn, status, runningTasksCount ]
    return [ None, None, None ]
    
def drainContainerInstance(containerInstanceArn, clusterName):
    resp = ecsClient.update_container_instances_state(
        cluster=clusterName,
        containerInstances=[
            containerInstanceArn
        ],
        status='DRAINING'
    )
def loopCheck(clusterName, containerInstanceArn, lifecycleHookName, asgGroupName, ec2InstanceId):
    def _emptyTasks():
        resp = ecsClient.list_tasks(
            cluster=clusterName,
            containerInstance=containerInstanceArn,
            desiredStatus='RUNNING'
        )
        pp(resp)
        return len(resp["taskArns"])==0
    for i in range(2):
        print("loop checking running tasks(#%d)" % i)
        if _emptyTasks():
            print("#%d GOOD - empty tasks" % i)
            # hook back to ASG lifecycle
            asg_complete_lifecycle(lifecycleHookName, asgGroupName, ec2InstanceId)
            return True
        else:
            print("#%d not empty, sleep 10s" % i)
            sys.stdout.flush()
            time.sleep(10)
    return False

def self_invoke(function_name, payload):
    if "has_retried" in payload:
        payload["has_retried"] +=1
    else:
        payload["has_retried"] = 1   

    resp = lambdaClient.invoke(
        FunctionName=function_name,
        InvocationType='Event',
        Payload=json.dumps(payload)    
    ) 
    print("lambda invoke respose: ",resp)   
    
def asg_complete_lifecycle(lifecycleHookName, asgGroupName, ec2InstanceId):
    try:
        resp = asgClient.complete_lifecycle_action(
            LifecycleHookName=lifecycleHookName,
            AutoScalingGroupName=asgGroupName,
            LifecycleActionResult='CONTINUE',
            InstanceId=ec2InstanceId)
        print("Response received from complete_lifecycle_action %s" % resp)
        print("Completedlifecycle hook action")
    except Exception as e:
        print(str(e))    

def lambda_handler(event, context):    
    print(event)
    function_name = context.function_name
    invoked_function_arn = context.invoked_function_arn
    is_complete = 0
    lifecyclehookname = None
    line = event['Records'][0]['Sns']['Message']
    message = json.loads(line)
    ec2InstanceId = message['EC2InstanceId']
    asgGroupName = message['AutoScalingGroupName']   

    if 'LifecycleTransition' in message.keys():
        if message['LifecycleTransition'].find('autoscaling:EC2_INSTANCE_TERMINATING') > -1:
            lifecycleHookName = message['LifecycleHookName']
            print("lifecycleHookName=%s" % lifecycleHookName) 

    clusterName = getClusterName()
    # print('got cluster %s' % clusterName)
    containerInstanceArns = getContainerInstances(clusterName)
    [ containerInstanceArn, status, runningTasksCount ] = getContainerInstanceId(clusterName, containerInstanceArns)
    if status=="DRAINING" and runningTasksCount==0:
        # already complete
        is_complete = 1
        print("DONE")
        # hook back to ASG lifecycle
        asg_complete_lifecycle(lifecycleHookName, asgGroupName, ec2InstanceId)
        return "DONE"
    elif status=="ACTIVE":
        print("status ACTIVE, drain it now")
        drainContainerInstance(containerInstanceArn, clusterName)
        if not loopCheck(clusterName, containerInstanceArn, lifecycleHookName, asgGroupName, ec2InstanceId):
            print("lookCheck failed - timeout.")
            return self_invoke(function_name, event)
    elif status=="DRAINING" and runningTasksCount!=0:
        print("draining now")
        if not loopCheck(clusterName, containerInstanceArn, lifecycleHookName, asgGroupName, ec2InstanceId):
            print("lookCheck failed - timeout.")
            return self_invoke(function_name, event)


# if __name__ == '__main__':
#     lambda_handler()


