# ECS Service Custom Metrics Logger
This Serverless App will create a complete serverless stack to periodically generate custom metrics to CloudWatch for Amazon ECS services.

At this moment, we support number of `Desired` tasks and number of `Running` tasks.


# Enable this feature with ecs-cfn-refarch

This is an optional stack for `ecs-cfn-refarch`(see [here](https://github.com/pahud/ecs-cfn-refarch/blob/0888b6898362e289434f5d02308a6551fad0fe4e/cloudformation/ecs.yaml#L313-L322)). To enable this support, simply pass `EnableEcsSvcCustomMetricsLogger=yes` to the `make` command

```bash
# enable the ecs-svc-custom-metrics-logger plugin
$ EnableEcsSvcCustomMetricsLogger=yes make create-ecs-cluster
```
