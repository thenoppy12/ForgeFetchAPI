import json
import xml.etree.ElementTree as Tree
from requests import get
from packaging.version import Version, InvalidVersion


def parse(xml_url: str, promotions_url: str):
    xml = Tree.fromstring(get(xml_url).content)
    promotions = get(promotions_url).json()["promos"]

    forge_versions = {}
    for game_version in xml.findall("./versioning/versions/version"):
        mc_version, forge_version = game_version.text.split("-", 1)
        base_url = f"https://maven.minecraftforge.net/net/minecraftforge/forge/{mc_version}-{forge_version}/forge-{mc_version}-{forge_version}"
        client_url = ""
        server_url = ""

        try:
            clean_version = Version(forge_version.split("-")[0])

            if Version("7.7.2.682") >= clean_version >= Version("4.0.0.183"):
                installer_url = f"{base_url}-universal.zip"
            elif clean_version <= Version("4.0.0.182"):
                client_url = f"{base_url}-client.zip"
                server_url = f"{base_url}-server.zip"
            else:
                installer_url = f"{base_url}-installer.jar"
        except InvalidVersion:
            print(f"Bad version formatting: {forge_version}, using default url, may be broken")
            installer_url = f"{base_url}-installer.jar"

        version_type = "release"
        if mc_version + "-latest" in promotions and forge_version == promotions[mc_version + "-latest"]:
            version_type = "latest"
        elif mc_version + "-recommended" in promotions and forge_version == promotions[mc_version + "-recommended"]:
            version_type = "recommended"

        if mc_version not in forge_versions:
            forge_versions[mc_version] = []

        if client_url == "" and server_url == "":
            forge_versions[mc_version].append({"id": forge_version, "type": version_type, "url": installer_url})
        else:
            forge_versions[mc_version].append({"id": forge_version, "type": version_type, "client_url": client_url, "server_url": server_url})

    ordered_keys = sorted(forge_versions, key=Version, reverse=True)
    return {key: forge_versions[key] for key in ordered_keys}


if __name__ == '__main__':
    xml_url = "https://maven.minecraftforge.net/net/minecraftforge/forge/maven-metadata.xml"
    promotions_url = "https://files.minecraftforge.net/net/minecraftforge/forge/promotions_slim.json"

    data = parse(xml_url, promotions_url)
    with open("web/version.json", "w") as file:
        file.write(json.dumps(data, indent=4))
