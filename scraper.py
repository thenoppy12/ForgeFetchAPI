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
        print(f"Processing Minecraft Version: {game_version}")

        page = requests.get(f"{url}/index_{game_version}.html")
        soup = BeautifulSoup(page.content, "html.parser")
        versions = soup.find("table", class_="download-list").find_all("td", class_="download-version")

        forge_versions[game_version] = []
        for v in versions:
            version_count += 1
            forge_version = v.text.replace("\n", "").replace(" ", "").split("Branch")[0]
            print(f"Found Forge Version: {forge_version}")
            forge_versions[game_version].append(forge_version)

    print(f"Complete! Found {version_count} Forge Versions.")
    return forge_versions


if __name__ == '__main__':
    data = scrape("https://files.minecraftforge.net/net/minecraftforge/forge/")
    with open("forge-versions.json", "w") as file:
        file.write(json.dumps(data, indent=4))
