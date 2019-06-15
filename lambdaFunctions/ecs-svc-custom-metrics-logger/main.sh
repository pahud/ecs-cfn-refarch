#!/bin/bash

export AWS_DEFAULT_REGION=$AWS_REGION
export AWS_REGION

result=($(aws --region $AWS_REGION ecs describe-services  \
--cluster $cluster \
--services $service \
--query 'services[0].[desiredCount,runningCount]' \
--output text))

desired=${result[0]}
running=${result[1]}

echo "desired=$desired running=$running"

aws --region $AWS_REGION cloudwatch put-metric-data \
--namespace ECS \
--metric-name Desired \
--dimensions Cluster=$cluster,Service=$service \
--timestamp $(date +%s) \
--value $desired \
--unit Count

aws --region $AWS_REGION cloudwatch put-metric-data \
--namespace ECS \
--metric-name Running \
--dimensions Cluster=$cluster,Service=$service \
--timestamp $(date +%s) \
--value $running \
--unit Count



