import json
import xml.etree.ElementTree as Tree
from requests import get
from packaging.version import Version


def parse(xml_url: str, promotions_url: str):
    xml = Tree.fromstring(get(xml_url).content)
    promotions = get(promotions_url).json()["promos"]

    forge_versions = {}
    for game_version in xml.findall("./versioning/versions/version"):
        mc_version, forge_version = game_version.text.split("-", 1)

        installer_url = f"https://maven.minecraftforge.net/net/minecraftforge/forge/{mc_version}-{forge_version}/forge-{mc_version}-{forge_version}-installer.jar"

        i = f"https://maven.minecraftforge.net/net/minecraftforge/forge/{mc_version}-{forge_version}/forge-{mc_version}-{forge_version}-universal.zip"

        version_type = "release"
        if mc_version + "-latest" in promotions and forge_version == promotions[mc_version + "-latest"]:
            version_type = "latest"
        elif mc_version + "-recommended" in promotions and forge_version == promotions[mc_version + "-recommended"]:
            version_type = "recommended"

        if mc_version not in forge_versions:
            forge_versions[mc_version] = []

        forge_versions[mc_version].append({"id": forge_version, "type": version_type, "url": installer_url})

    ordered_keys = sorted(forge_versions, key=Version, reverse=True)
    return {key: forge_versions[key] for key in ordered_keys}


if __name__ == '__main__':
    xml_url = "https://maven.minecraftforge.net/net/minecraftforge/forge/maven-metadata.xml"
    promotions_url = "https://files.minecraftforge.net/net/minecraftforge/forge/promotions_slim.json"

    data = parse(xml_url, promotions_url)

    print(data.keys())

    with open("web/forge-versions.json", "w") as file:
        file.write(json.dumps(data, indent=4))
