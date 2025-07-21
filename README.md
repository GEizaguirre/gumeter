# gumeter

##  A benchmarking suite for serverless platform elasticity.

A member of the [PyRun](https://pyrun.cloud/) and [Lithops](https://lithops-cloud.github.io/) serverless stack. Refined from the original [Lithops application repository](https://github.com/lithops-cloud/applications).

## Reproducing paper results

```bash
pip install .

gumeter deploy aws_lambda
gumeter deploy gcp_cloudrun
gumeter deploy code_engine

gumeter warm-up aws_lambda
gumeter run-all aws_lambda
gumeter warm-up gcp_cloudrun
gumeter run-all gcp_cloudrun
gumeter warm-up code_engine
gumeter run-all code_engine
```
