import json
from lithops import config

from gumeter.utils import _run_command


REDIS_CLUSTER_ID = "gumeter-redis-cluster"
NODE_TYPE = "cache.m5.large"
REDIS_OSS_VERSION = "7.0"
REDIS_PORT = 6379
REDIS_AUTH_TOKEN = "gumeter-password123!"


def extract_deploy_config():

    exec_config = {}
    lithops_config = config.default_config()
    lambda_config = lithops_config.get('aws_lambda', {})
    exec_config["region"] = lambda_config.get("region")
    vpc_config = lambda_config.get("vpc", {})
    exec_config["security_groups"] = vpc_config.get("security_groups")
    exec_config["subnets"] = vpc_config.get("subnets")

    return exec_config


def deploy_single_node_redis_elasticache(
    region: str,
    existing_subnet_id: str,
    existing_security_group_id: str,
    redis_cluster_id: str,
    node_type: str,
    redis_engine_version: str,
    redis_port: int,
    redis_auth_token: str
):

    print("--- Starting Single-Node Redis ElastiCache Deployment Script ---")
    print(f"Region: {region}")
    print(f"Using Existing Subnet ID: {existing_subnet_id}")
    print(f"Using Existing Security Group ID: {existing_security_group_id}")

    subnet_group_name = f"redis-subnet-group-{redis_cluster_id}"

    print("1. Checking/Creating ElastiCache Subnet Group...")

    try:
        _run_command(
            [
                "aws", "elasticache", "describe-cache-subnet-groups",
                "--cache-subnet-group-name", subnet_group_name,
                "--region", region
            ],
            out=True
        )
        print(
            f"ElastiCache Subnet Group '{subnet_group_name}' already exists.",
            "Skipping creation."
        )
    except Exception:
        print(f"Subnet group '{subnet_group_name}' not found. Creating...")
        try:
            _run_command(
                [
                    "aws", "elasticache", "create-cache-subnet-group",
                    "--cache-subnet-group-name", subnet_group_name,
                    "--subnet-ids", existing_subnet_id,
                    "--cache-subnet-group-description", f"Subnet group for {redis_cluster_id}",
                    "--region", region
                ]
            )
            print(f"ElastiCache Subnet Group Created: {subnet_group_name}")
        except Exception as e:
            print(
                "Error: Failed to create ElastiCache Subnet Group.",
                f"Details: {e}"
            )
            return False

    print(
        "2. Creating ElastiCache Single-Node Redis Cluster"
        f"({redis_cluster_id})..."
    )
    print("  This might take 5-10 minutes to become available.")

    command = [
        "aws", "elasticache", "create-replication-group",
        "--replication-group-id", redis_cluster_id,
        "--replication-group-description", f"Redis cluster {redis_cluster_id}",
        "--engine", "redis",
        "--cache-node-type", node_type,
        "--engine-version", redis_engine_version,
        "--num-node-groups", "1",
        "--replicas-per-node-group", "0",
        "--transit-encryption-enabled",
        "--auth-token", redis_auth_token,
        "--security-group-ids", existing_security_group_id,
        "--cache-subnet-group-name", subnet_group_name,
        "--port", str(redis_port),
        "--region", region
    ]

    try:
        _run_command(command)
    except Exception as e:
        print(f"Error: {e}")
        return False

    print(
        "ElastiCache Redis Cluster creation initiated.",
        "Waiting for it to become 'available'..."
    )

    print("3. Waiting for cluster to be available and retrieving endpoint...")

    try:
        _run_command(
            [
                "aws", "elasticache", "wait", "replication-group-available",
                "--replication-group-id", redis_cluster_id,
                "--region", region
            ],
            out=False
        )
    except Exception as e:
        print(
            "Error: Failed to wait for cluster availability.",
            f"Details: {e}"
        )
        return False

    print("ElastiCache Redis Cluster is now AVAILABLE!")

    try:
        cluster_info_json = _run_command(
            [
                "aws", "elasticache", "describe-replication-groups",
                "--replication-group-id", redis_cluster_id,
                "--query", "ReplicationGroups[0].NodeGroups[0].PrimaryEndpoint",
                "--output", "json",
                "--region", region
            ],
            out=True
        )
    except Exception as e:
        print(
            "Error: Failed to retrieve cluster endpoint.",
            f"Details: {e}"
        )
        return False

    try:
        endpoint_info = json.loads(cluster_info_json)
        redis_endpoint = endpoint_info.get('Address')
        redis_port_actual = endpoint_info.get('Port')
    except json.JSONDecodeError:
        print(
            "Error: Failed to parse JSON output for endpoint:"
            f"{cluster_info_json}"
        )
        return False

    print("\n--- Redis Cluster Details ---")
    print(f"Redis Cluster ID: {redis_cluster_id}")
    print(f"Primary Endpoint: {redis_endpoint}")
    print(f"Port:             {redis_port_actual}")
    print(f"Auth Token:       {redis_auth_token}")

    print(
        "You can connect using redis-cli",
        "(from an AWS instance in the same VPC/SG) with:"
    )
    print(
        f"redis-cli -h {redis_endpoint} -p {redis_port_actual} -a",
        f"\"{redis_auth_token}\" --tls"
    )

    return True


def delete_elasticache(
    redis_cluster_id: str,
    subnet_group_name: str,
    region: str
):

    pass


def deploy_elasticache():

    deploy_config = extract_deploy_config()
    deploy_single_node_redis_elasticache(
        region=deploy_config["region"],
        existing_subnet_id=deploy_config["subnets"][0],
        existing_security_group_id=deploy_config["security_groups"][0],
        redis_cluster_id=REDIS_CLUSTER_ID,
        node_type=NODE_TYPE,
        redis_engine_version=REDIS_OSS_VERSION,
        redis_port=REDIS_PORT,
        redis_auth_token=REDIS_AUTH_TOKEN
    )


if __name__ == "__main__":
    deploy_elasticache()
