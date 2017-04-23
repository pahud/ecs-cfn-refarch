# ecs-cfn-refarch

## service-only 
This cloudformation template will provision common Amazon ECS infrastructure including:

- VPC, IGW, subnets, routing tables, security groups
- IAM role
- Autoscaling Group and Launch Configuration
- Lambda function as custom resource to query latest ECS AMI ID
- ECS Service, Cluster, Task Definition
- [Caddy](https://caddyserver.com/) as the default web server


click the button to launch the demo stack in *us-west-2*

[![cloudformation-launch-stack](https://s3.amazonaws.com/cloudformation-examples/cloudformation-launch-stack.png)](https://console.aws.amazon.com/cloudformation/home?region=us-west-2#/stacks/new?stackName=ecs-refarch&templateURL=https://s3-us-west-2.amazonaws.com/pahud-cfn-us-west-2/ecs-cfn-refarch/cloudformation/service.yml)

check the cloudformation output and click the ***LoadBalancerURL*** link to see the result.



### Notice

- By default this template will create on-demand instance. If you need spot instance instead, specify ***SpotPrice*** parameter, e.g.  "**0.1**"



## complete stack for CI/CD with Amazon ECS



#### 1. Fork the GitHub repository

[Fork](https://help.github.com/articles/fork-a-repo/) this GitHub repository(https://github.com/pahud/ecs-cfn-refarch) into your GitHub account.

From your terminal application, execute the following command (make sure to replace `<your_github_username>` with your actual GitHub username):

```
git clone https://github.com/<your_github_username>/ecs-cfn-refarch
```

This creates a directory named `ecs-cfn-refarch` in your current directory, which contains the code for the Amazon ECS sample app unser `src` directory.



#### 2. Create the CloudFormation stack

click the button to launch the demo stack in *us-west-2*

[![cloudformation-launch-stack](https://s3.amazonaws.com/cloudformation-examples/cloudformation-launch-stack.png)](https://console.aws.amazon.com/cloudformation/home?region=us-west-2#/stacks/new?stackName=ecs-refarch&templateURL=https://s3-us-west-2.amazonaws.com/pahud-cfn-us-west-2/ecs-cfn-refarch/cloudformation/codepipeline.yml)



The CloudFormation template requires the following parameters:

- GitHub configuration
  - **CodeBuildEnvironment**: CodeBuild environment. 
  - **GitHubBranch**: The branch of the repo to deploy continuously. Leave it as default "master"
  - **GitHubRepo**: The name of the github repo to  deploy continuously. Leave it as default "ecs-cfn-refarch"
  - **GitHubToken**: Token for the user specified above. ([https://github.com/settings/tokens](https://github.com/settings/tokens))
  - **GitHubUser**: Your username on GitHub.
  - **ServiceName**: Your ECS Service name.
  - **UseCodeCommit**: If you use CodeCommit instead, select **"yes"** and ignore all GithHub parameters above.