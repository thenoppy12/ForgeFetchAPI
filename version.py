from requests import get


def process_versions(api_url: str):
    versions = get(api_url).json()

    for version in versions.keys():
