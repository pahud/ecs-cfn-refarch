# ecs-cfn-refarch

This cloudformation template will provision common Amazon ECS infrastructure including:

- VPC, IGW, subnets, routing tables, security groups
- IAM role
- Autoscaling Group and Launch Configuration
- Lambda function as custom resource to query latest ECS AMI ID
- ECS Service, Cluster, Task Definition


click the button to launch the demo stack in us-west-2

[![cloudformation-launch-stack](https://s3.amazonaws.com/cloudformation-examples/cloudformation-launch-stack.png)](https://console.aws.amazon.com/cloudformation/home?region=us-west-2#/stacks/new?stackName=ECS-basic&templateURL=https://s3-us-west-2.amazonaws.com/pahud-cfn-us-west-2/cfn.yaml)


check the cloudformation output and click the ***LoadBalancerURL*** link to see the result.



