# gumeter

##  A benchmarking suite for serverless platform elasticity.

A member of the [PyRun](https://pyrun.cloud/) and [Lithops](https://lithops-cloud.github.io/) serverless stack. Refined from the original [Lithops application repository](https://github.com/lithops-cloud/applications).

## Reproducing paper results

```bash
pip install .

gumeter deploy aws_lambda
gumeter deploy aws_batch
gumeter deploy gcp_cloudrun
gumeter deploy code_engine

gumeter warm-up --backend aws_lambda
gumeter run-all --backend aws_lambda
gumeter warm-up --backend aws_batch
gumeter run-all --backend aws_batch
gumeter warm-up --backend gcp_cloudrun
gumeter run-all --backend gcp_cloudrun
gumeter warm-up --backend code_engine
gumeter run-all --backend code_engine
```
