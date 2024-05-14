import requests
def create_new_token():
    """Создание нового токена"""
    metadata_url = "http://169.254.169.254/computeMetadata/v1/instance/service-accounts/default/token"
    headers = {"Metadata-Flavor": "Google"}
    response = requests.get(metadata_url, headers=headers)
    token = response.json()["access_token"]
    return token
