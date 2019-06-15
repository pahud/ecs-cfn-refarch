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
# modify this as your own S3 temp bucket. Make sure your locak IAM user have read/write access
S3BUCKET	?= pahud-tmp-ap-northeast-1
LAMBDA_REGION ?= ap-northeast-1
STACKNAME	?= ecs-stats-logger
LAMBDA_FUNC_NAME ?= $(STACKNAME)

	
.PHONY: all
all: func-prep sam-package sam-deploy

.PHONY: func-prep
func-prep:
	@rm -rf ./func.d; mkdir ./func.d
	@cp main.sh bootstrap func.d/ && chmod +x ./func.d/bootstrap ./func.d/main.sh

.PHONY: sam-package
sam-package:
	@docker run -ti \
	-v $(PWD):/home/samcli/workdir \
	-v $(HOME)/.aws:/home/samcli/.aws \
	-w /home/samcli/workdir \
	-e AWS_DEFAULT_REGION=$(LAMBDA_REGION) \
	pahud/aws-sam-cli:latest sam package --template-file sam.yaml --s3-bucket $(S3BUCKET) --output-template-file packaged.yaml

.PHONY: sam-sar-package
sam-sar-package:
	@docker run -ti \
	-v $(PWD):/home/samcli/workdir \
	-v $(HOME)/.aws:/home/samcli/.aws \
	-w /home/samcli/workdir \
	-e AWS_DEFAULT_REGION=$(LAMBDA_REGION) \
	pahud/aws-sam-cli:latest sam package --template-file sam-sar.yaml --s3-bucket $(S3BUCKET) --output-template-file packaged.yaml


.PHONY: sam-package-from-sar
sam-package-from-sar: sam-sar-package


.PHONY: sam-publish
sam-publish:
	@docker run -ti \
	-v $(PWD):/home/samcli/workdir \
	-v $(HOME)/.aws:/home/samcli/.aws \
	-w /home/samcli/workdir \
	-e AWS_DEFAULT_REGION=$(LAMBDA_REGION) \
	pahud/aws-sam-cli:latest sam publish --region $(LAMBDA_REGION) --template packaged.yaml


.PHONY: sam-deploy	
sam-deploy:
	@aws --region $(LAMBDA_REGION)  cloudformation deploy \
	--parameter-overrides cluster=$(cluster) service=$(service) \
	--template-file ./packaged.yaml --stack-name "$(LAMBDA_FUNC_NAME)" --capabilities CAPABILITY_IAM CAPABILITY_AUTO_EXPAND CAPABILITY_NAMED_IAM
	# print the cloudformation stack outputs
	@aws --region $(LAMBDA_REGION) cloudformation describe-stacks --stack-name "$(LAMBDA_FUNC_NAME)" --query 'Stacks[0].Outputs'

.PHONY: sam-logs-tail
sam-logs-tail:
	sam logs --name $(LAMBDA_FUNC_NAME) --tail
	# @docker run -ti \
	# -v $(PWD):/home/samcli/workdir \
	# -v $(HOME)/.aws:/home/samcli/.aws \
	# -w /home/samcli/workdir \
	# -e AWS_DEFAULT_REGION=$(LAMBDA_REGION) \
	# -e AWS_REGION=$(LAMBDA_REGION) \
	# pahud/aws-sam-cli:latest sam logs --name eks-lambda-drainer --tail --debug

.PHONY: sam-destroy
sam-destroy:
	# destroy the stack now
	@aws --region $(LAMBDA_REGION) cloudformation delete-stack --stack-name "$(LAMBDA_FUNC_NAME)"
	# deleting the stack. check your cloudformaion console to make sure stack is completely deleted

