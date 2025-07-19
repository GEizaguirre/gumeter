import json
import os


def get_docker_username_from_config():
    config_path = os.path.expanduser("~/.docker/config.json")
    if not os.path.exists(config_path):
        return None

    try:
        with open(config_path, 'r') as f:
            config = json.load(f)

        if (
            'auths' in config
            and 'https://index.docker.io/v1/' in config['auths']
        ):
            auth_info = config['auths']['https://index.docker.io/v1/']
            if 'auth' in auth_info:
                # 'auth' is base64 encoded "username:password"
                import base64
                decoded_auth = base64.b64decode(
                    auth_info['auth']
                ).decode('utf-8')
                username = decoded_auth.split(':')[0]
                return username

    except (json.JSONDecodeError, KeyError) as e:
        print(f"Error reading Docker config: {e}")
        return None
    return None
