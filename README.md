# gumeter

##  A benchmarking suite for serverless platform elasticity.

A member of the [PyRun](https://pyrun.cloud/) and [Lithops](https://lithops-cloud.github.io/) serverless stack. Refined from the original [Lithops application repository](https://github.com/lithops-cloud/applications).

## Applications overview
<img width="1112" height="528" alt="image" src="https://github.com/user-attachments/assets/fed5112e-5a68-4959-922a-9b58ecce4596" />

## Supported compute backends
| Platform     | Cloud Provider | Service Type     | Storage Backend            |
|--------------|----------------|------------------|----------------------------|
| Lambda       | AWS            | *FaaS*           | AWS S3                     |
| Cloud Run    | GCP            | *CaaS* / *FaaS*  | GCP Cloud Storage          |
| Code Engine  | IBM Cloud      | *CaaS*           | IBM Cloud Object Storage   |

## Installation and setup 
Ensure you have Python 3.10, Docker engine and git command-line interface installed. To complete the installation, clone the repository and install the dependencies (we strongly recommend using a virtual environment):

```bash
git clone --recurse-submodules https://github.com/GEizaguirre/gumeter.git

cd gumeter
python3 -m venv .venv
source .venv/bin/activate
pip install .

# Verify installation
gumeter version
```

## Cloud environment configuration 
Gumeter operates on serverless engines provided by AWS, GCP, and IBM Cloud through Lithops, and for this purpose, we need to define the corresponding Lithops configuration. The configuration must be specified in the file `∼/.lithops/config`, to which the following content should be added.

```yaml
# AWS CONFIGURATION
aws:
    access_key_id: <ACCESS_KEY_ID>
    secret_access_key: <SECRET_ACCESS_KEY>
    session_token: <SESSION_TOKEN>
    region: us-east-1
aws_lambda:
    execution_role: <EXECUTION_ROLE> # See: lithops-cloud.github.io/docs/source/compute_config/aws_lambda.html
# GOOGLE CLOUD PLATFORM CONFIGURATION
gcp:
    credentials_path: <CREDENTIALS_PATH> # Path to service account JSON
    region: us-east1
gcp_cloudrun:
    max_workers: 200
    runtime_cpu: 1
    runtime_include_function: false
    runtime_memory: 2048
# IBM CLOUD CONFIGURATION
ibm:
    iam_api_key: <IAM_API_KEY>
    region: us-east
    resource_group_id: <RESOURCE_GROUP_ID>
ibm_cos:
    service_instance_id : <SERVICE_INSTANCE_ID> # The COS instance CRN
code_engine:
    docker_server: docker.io
    docker_user: <DOCKER_USER>
    runtime_cpu: 1
    runtime_include_function: false
    runtime_memory: 2048
```
All placeholders (terms enclosed in angle brackets <...>) must be replaced with the corresponding entities of the selected cloud provider. These placeholders represent the minimal linkage required to connect to the cloud providers (e.g., access keys for AWS, credentials file for GCP, etc.) as well as the minimal Lithops configuration to use these serverless platforms.

## Install dependencies and prepare data
```bash
gumeter init
```

## Deploy the execution runtimes
```bash
# Deploy to AWS Lambda
gumeter deploy aws_lambda

# Deploy to Google Cloud Run
gumeter deploy gcp_cloudrun

# Deploy to IBM Code Engine
gumeter deploy code_engine
```

## Execute the serverless applications
```bash
# AWS Lambda execution
gumeter warmup aws_lambda
gumeter run-all aws_lambda

# Google Cloud Run execution
gumeter warmup gcp_cloudrun
gumeter run-all gcp_cloudrun

# IBM Code Engine execution
gumeter warmup code_engine
gumeter run-all code_engine
```

## Data visualization
In the `plots/paper/` folder, we provide the scripts that generate the figures presented in the paper: running the indicated scripts is enough to reproduce the original plots.

### IBM Code Engine
