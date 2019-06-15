# ECS Service Custom Metrics Logger
Amazon ECS has some buit-in service-level cloudwatch metrics, however, some metrics are still missing such as `number of desired task number` and `number of running task number`. We build this serverless app to help you automatically generate those missing metrics as a **Serverless App** hosting in **SAR(Serverless App Repository)** in AWS. And you can optionally enable this feature by simply passing an argument to your `make` command.


This Serverless App will create a complete serverless stack to periodically generate custom metrics to CloudWatch for Amazon ECS services.

At this moment, we support number of `Desired` tasks and number of `Running` tasks to help you create a sophisticated dashboard like this:
![img](https://pbs.twimg.com/media/D8hBR1SUwAEGNFE.jpg)


# Enable this feature with ecs-cfn-refarch

This is an optional stack for `ecs-cfn-refarch`(see [here](https://github.com/pahud/ecs-cfn-refarch/blob/0accf60b1c1a3080467c7bfa0da623a6523afcf2/cloudformation/ecs.yaml#L313-L322)). To enable this support, simply pass `EnableEcsSvcCustomMetricsLogger=yes` to the `make` command

```bash
# enable the ecs-svc-custom-metrics-logger plugin
$ EnableEcsSvcCustomMetricsLogger=yes make create-ecs-cluster
```
