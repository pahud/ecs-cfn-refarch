SECRETS_FILE ?= secrets.mk
ifeq ($(shell test -e $(SECRETS_FILE) && echo -n yes),yes)
    include $(SECRETS_FILE)
endif
CUSTOM_FILE ?= custom.mk
ifeq ($(shell test -e $(CUSTOM_FILE) && echo -n yes),yes)
    include $(CUSTOM_FILE)
endif
ROOT ?= $(shell pwd)
AWS_ACCOUNT_ID := $(shell aws sts get-caller-identity --query 'Account' --output text)
YAML_BRANCH ?= stable
ECS_YAML_URL ?= https://s3-us-west-2.amazonaws.com/pahud-cfn-us-west-2/ecs-cfn-refarch/cloudformation/ecs-$(YAML_BRANCH).yaml
CLUSTER_STACK_NAME ?= ecsdemo
CLUSTER_NAME ?= $(CLUSTER_STACK_NAME)
REGION ?= ap-northeast-1
SSH_KEY_NAME ?= 'aws-pahud'
VPC_ID ?= vpc-e549a281
SUBNET1 ?= subnet-05b643f57a6997deb
SUBNET2 ?= subnet-09e79eb1dec82b7e2
SUBNET3 ?= subnet-0c365d97cbc75ceec
OnDemandBaseCapacity ?= 0
NodeAutoScalingGroupMinSize ?= 0
NodeAutoScalingGroupDesiredSize ?= 2
NodeAutoScalingGroupMaxSize ?= 5
ASGAutoAssignPublicIp ?= yes
InstanceTypesOverride ?= 't3.medium,t3.large,t3.xlarge'
EnableEcsSvcCustomMetricsLogger ?= no



# all: deploy

# deploy:
# 	#aws --region us-west-2 s3 cp cloudformation s3://pahud-cfn-us-west-2/ecs-cfn-refarch/cloudformation/ --acl public-read --recursive
# 	aws --region us-west-2 s3 sync cloudformation s3://pahud-cfn-us-west-2/ecs-cfn-refarch/cloudformation/ --acl public-read

.PHONY: update-yaml
update-stable-yaml:
	@aws --region us-west-2 s3 cp cloudformation/ecs.yaml s3://pahud-cfn-us-west-2/ecs-cfn-refarch/cloudformation/ecs-stable.yaml --acl public-read
	@aws --region us-west-2 s3 cp cloudformation/service.yaml s3://pahud-cfn-us-west-2/ecs-cfn-refarch/cloudformation/service-stable.yaml --acl public-read
	@aws --region us-west-2 s3 cp cloudformation/ecs-svc-custom-metrics-logger.yaml s3://pahud-cfn-us-west-2/ecs-cfn-refarch/cloudformation/ecs-svc-custom-metrics-logger-stable.yaml --acl public-read
	@aws --region us-west-2 s3 cp cloudformation/awscli-lambda-layer.yaml s3://pahud-cfn-us-west-2/ecs-cfn-refarch/cloudformation/awscli-lambda-layer-stable.yaml  --acl public-read

.PHONY: update-dev-yaml	
update-dev-yaml: 
	@aws --region us-west-2 s3 cp cloudformation/ecs.yaml s3://pahud-cfn-us-west-2/ecs-cfn-refarch/cloudformation/ecs-dev.yaml --acl public-read
	@aws --region us-west-2 s3 cp cloudformation/service.yaml s3://pahud-cfn-us-west-2/ecs-cfn-refarch/cloudformation/service-dev.yaml --acl public-read
	@aws --region us-west-2 s3 cp cloudformation/ecs-svc-custom-metrics-logger.yaml s3://pahud-cfn-us-west-2/ecs-cfn-refarch/cloudformation/ecs-svc-custom-metrics-logger-dev.yaml --acl public-read
	@aws --region us-west-2 s3 cp cloudformation/awscli-lambda-layer.yaml s3://pahud-cfn-us-west-2/ecs-cfn-refarch/cloudformation/awscli-lambda-layer-dev.yaml  --acl public-read


.PHONY: create-cluster
create-ecs-cluster:
	@aws --region $(REGION) cloudformation create-stack --template-url $(ECS_YAML_URL) \
	--stack-name  $(CLUSTER_STACK_NAME) \
	--capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM CAPABILITY_AUTO_EXPAND \
	--parameters \
	ParameterKey=YamlBranch,ParameterValue="$(YAML_BRANCH)" \
	ParameterKey=EnableEcsSvcCustomMetricsLogger,ParameterValue="$(EnableEcsSvcCustomMetricsLogger)" \
	ParameterKey=VpcId,ParameterValue="$(VPC_ID)" \
	ParameterKey=SshKeyName,ParameterValue="$(SSH_KEY_NAME)" \
	ParameterKey=OnDemandBaseCapacity,ParameterValue="$(OnDemandBaseCapacity)" \
	ParameterKey=ASGMinSize,ParameterValue="$(NodeAutoScalingGroupMinSize)" \
	ParameterKey=ASGDesiredCapacity,ParameterValue="$(NodeAutoScalingGroupDesiredSize)" \
	ParameterKey=ASGMaxSize,ParameterValue="$(NodeAutoScalingGroupMaxSize)" \
	ParameterKey=InstanceTypesOverride,ParameterValue="$(InstanceTypesOverride)" \
	ParameterKey=ASGAutoAssignPublicIp,ParameterValue="$(ASGAutoAssignPublicIp)" \
	ParameterKey=SubnetIds,ParameterValue=$(SUBNET1)\\,$(SUBNET2)\\,$(SUBNET3)
	@echo click "https://console.aws.amazon.com/cloudformation/home?region=$(REGION)#/stacks to see the details"
	

.PHONY: update-ecs-cluster	
update-ecs-cluster:
	@aws --region $(REGION) cloudformation update-stack --template-url $(ECS_YAML_URL) \
	--stack-name  $(CLUSTER_STACK_NAME) \
	--capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM CAPABILITY_AUTO_EXPAND \
	--parameters \
	ParameterKey=YamlBranch,ParameterValue="$(YAML_BRANCH)" \
	ParameterKey=EnableEcsSvcCustomMetricsLogger,ParameterValue="$(EnableEcsSvcCustomMetricsLogger)" \
	ParameterKey=VpcId,ParameterValue="$(VPC_ID)" \
	ParameterKey=SshKeyName,ParameterValue="$(SSH_KEY_NAME)" \
	ParameterKey=OnDemandBaseCapacity,ParameterValue="$(OnDemandBaseCapacity)" \
	ParameterKey=ASGMinSize,ParameterValue="$(NodeAutoScalingGroupMinSize)" \
	ParameterKey=ASGDesiredCapacity,ParameterValue="$(NodeAutoScalingGroupDesiredSize)" \
	ParameterKey=ASGMaxSize,ParameterValue="$(NodeAutoScalingGroupMaxSize)" \
	ParameterKey=InstanceTypesOverride,ParameterValue="$(InstanceTypesOverride)" \
	ParameterKey=ASGAutoAssignPublicIp,ParameterValue="$(ASGAutoAssignPublicIp)" \
	ParameterKey=SubnetIds,ParameterValue=$(SUBNET1)\\,$(SUBNET2)\\,$(SUBNET3)
	

.PHONY: get-ecs-cluster	
get-ecs-cluster:
	@aws --region $(REGION) cloudformation describe-stacks \
	--stack-name  $(CLUSTER_STACK_NAME) \
	--query "Stacks[0].Outputs" --output json

.PHONY: describe-ecs-cluster	
describe-ecs-cluster: get-ecs-cluster	

.PHONY: delete-ecs-cluster	
delete-ecs-cluster:
	@aws --region $(REGION) cloudformation delete-stack --stack-name "$(CLUSTER_STACK_NAME)"
	@echo "deleting the stacks now."
	@echo click "https://console.aws.amazon.com/cloudformation/home?region=$(REGION)#/stacks to make sure the stacks were deleted"

clean:
	echo "done"


.PHONY: all deploy clean
