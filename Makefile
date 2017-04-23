.PHONY: all deploy clean

all: deploy

deploy:
	#aws --region us-west-2 s3 cp cloudformation s3://pahud-cfn-us-west-2/ecs-cfn-refarch/cloudformation/ --acl public-read --recursive
	aws --region us-west-2 s3 sync cloudformation s3://pahud-cfn-us-west-2/ecs-cfn-refarch/cloudformation/ --acl public-read

clean:
	echo "done"
