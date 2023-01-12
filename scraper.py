import requests
from bs4 import BeautifulSoup
import json


def scrape(url: str):
    version_count = 0
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")

    supported_game_versions = []
    for version in soup.find_all("li", class_="li-version-list"):
        for element in version.find_all("li"):
            supported_game_versions.append(element.text.replace("\n", ""))

    forge_versions = {}
    for game_version in supported_game_versions:
        # Temp solution as format for 1.5.1 and below is different
        if game_version == "1.5.1":
            break

        print(f"Processing Minecraft Version: {game_version}")

        # Get page data
        page = requests.get(f"{url}/index_{game_version}.html")
        soup = BeautifulSoup(page.content, "html.parser")
        versions = soup.find("table", class_="download-list").find_all("td", class_="download-version")

        # Process all version on page
        forge_versions[game_version] = []
        for v in versions:
            version_count += 1
            forge_version = v.text.replace("\n", "").replace(" ", "").split("Branch")[0]
            installer_url = f"https://maven.minecraftforge.net/net/minecraftforge/forge/{game_version}-{forge_version}/forge-{game_version}-{forge_version}-installer.jar"

            # Figure out version type
            version_type = v.find("i", class_="promo-latest")
            if version_type is not None:
                version_type = "latest"
            elif v.find("i", class_="promo-recommended") is not None:
                version_type = "recommended"
            else:
                version_type = "release"

            print(f"Found Forge Version: {forge_version} : {installer_url}")
            forge_versions[game_version].append({"id": forge_version, "type": version_type, "url": installer_url})

    print(f"Complete! Found {version_count} Forge Versions.")
    return forge_versions


if __name__ == '__main__':
    data = scrape("https://files.minecraftforge.net/net/minecraftforge/forge/")
    with open("forge-versions.json", "w") as file:
        file.write(json.dumps(data, indent=4))
