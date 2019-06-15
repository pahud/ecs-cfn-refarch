# ecs-cfn-refarch

This is an **Amazon EC2 Container Service** reference architecture with cloudformation templates that helps you provision a complete Amazon ECS environment with many advanced optional features.

![](Images/ecs-cfn-refarch.png)



## Features

- [x] Cluster provisioned with **mixed autoscaling group**(ondemand + spot instances diversified across many types and AZs)
- [x] Secrets saved in SSM **Parameter Store**
- [x] Using latest Amazon ECS AMI
- [x] Built-in **service autoscaling** policies and **cluster autoscaling** policies
- [x] Support [ECS Service Custom Metrics Logger](https://github.com/pahud/ecs-cfn-refarch/tree/master/lambdaFunctions/ecs-svc-custom-metrics-logger) as a plug-in to automatically generate some missing metrics

# Prerequisite

`ecs-cfn-refarch` will not generate the following resources for you. Make sure you have created them.

- [x] A VPC with 3 public subnets
- [x] A SSH key pair in EC2 console 



# Usage

create a `custom.mk` file and customize your parameters in this file

```bash
# git clone the project
$ git clone https://github.com/pahud/ecs-cfn-refarch.git
$ cd ecs-cfn-refarch
$ cp custom.mk.sample custom.mk
$ vim custom.mk
```

Create the cluster

```bash
# create the cluster
$ make create-ecs-cluster
```

click the link to the cloudformation console. The whole stack should be created in 5–7minutes.

# Validate

When the cloudformation is completed. Check the stach output:

```bash
# check the stack output
$ make describe-ecs-cluster
```

Response

```json
[
    {
        "OutputKey": "GreetingURL", 
        "OutputValue": "http://ecsdemo-MAIN-1M6ASY034M08X-alb-2131750000.ap-northeast-1.elb.amazonaws.com/greeting.html"
    },  
    {
        "OutputKey": "URL", 
        "OutputValue": "http://ecsdemo-MAIN-1M6ASY034M08X-alb-2131750000.ap-northeast-1.elb.amazonaws.com"
    }
]
```

click the `URL` and you'll see the phpinfo page, wihch is served by ECS Tasks behind ALB.



![](Images/phpinfo.png)



If you cURL the `GreetingURL` , you'll get a static page containing credentials stored in SSM Parameter Store(i.e.`ECSYourName` and `ECSYourPassword`). The credentials were retrieved by ECS Execution Role from SSM Parameter on task bootstrapping and is injected into the environment variables.([details](https://github.com/pahud/ecs-cfn-refarch/blob/91424203d946561c6098992d67cc41d87de9ee89/cloudformation/service.yaml#L1312-L1314))

```bash
$ curl http://ecsdemo-MAIN-1M6ASY034M08X-alb-2131750000.ap-northeast-1.elb.amazonaws.com/greeting.html
<!DOCTYPE html>
<html>
<head>
<title>EC2 Parameter Store demo</title>
</head>
<body>
<p>
<h1>Hi DefaultName!</h1>
<p>
<h2>Your password is DefaultPassword!</h2>
```

# attributes
By default, instances will have `instance-purchase-option` attributes either `ondemand` or `spot`([implementation detail](https://github.com/pahud/ecs-cfn-refarch/blob/96566d2e585f081bd5a4e281d64e9ff5f2acc6d1/cloudformation/service.yaml#L1135-L1142)).

For example, list all the instances with `instance-purchase-option=spot`:
```bash
$ aws ecs list-attributes --target-type container-instance  --region ap-northeast-1  --cluster ecsdemo-MAIN-IKGTIS1HXS9J-ecs-cluster --attribute-name instance-purchase-option --attribute-value spot
{
    "attributes": [
        {
            "targetId": "arn:aws:ecs:ap-northeast-1:903779448426:container-instance/22119ce6-bcfc-488d-ba8a-d005f2f6237f", 
            "name": "instance-purchase-option", 
            "value": "spot"
        }, 
        {
            "targetId": "arn:aws:ecs:ap-northeast-1:903779448426:container-instance/0dbf6399-e51d-4fe7-a6b8-c86019d101bc", 
            "name": "instance-purchase-option", 
            "value": "spot"
        }, 
        {
            "targetId": "arn:aws:ecs:ap-northeast-1:903779448426:container-instance/097bec0a-11c2-4c5a-8231-b82f387574ce", 
            "name": "instance-purchase-option", 
            "value": "spot"
        }
    ]
}
```

Optionally, you may define your [task placement constraints](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/task-placement-constraints.html) to explicitly deploy
ECS tasks on `ondemand` or `spot`.

```json
"placementConstraints": [
    {
        "expression": "attribute:instance-purchase-option == spot",
        "type": "memberOf"
    }
]
```

This will give you better control over the taks placement based on the constraints expression.



# clean up

```bash
# delete the stacks
$ make delete-ecs-cluster
```

