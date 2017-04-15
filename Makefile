.PHONY: all deploy clean

all: deploy

deploy:
	aws --region us-west-2 s3 cp cfn.yaml s3://pahud-cfn-us-west-2/

clean:
	echo "done"
