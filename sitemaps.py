from typing import List

import pandas as pd
import requests
from bs4 import BeautifulSoup

PUBLIC_SITEMAP_URL = "https://public.fr/sitemap_index.xml"
VSD_SITEMAP_URL = "https://vsd.fr/sitemap_index.xml"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"
}


def get_sitemaps(url, **kwargs) -> List[str]:
    """
    Get available sitemaps from the URL based on whether it's a sitemap url or not.
    """
    try:
        response = requests.get(url, headers=HEADERS)
        soup = BeautifulSoup(response.content, "xml")

        if "sitemap" in kwargs:
            urls = [loc.text for loc in soup.find_all("loc")]
        else:
            urls = [loc.text for loc in soup.find_all("loc") if loc.parent.name == "url"]
        print(f"{url} :", len(urls))
        return urls
    except Exception as e:
        print("Exception Error:", e)
        return []


if __name__ == "__main__":
    # Get sitemap links
    srcs = [PUBLIC_SITEMAP_URL, VSD_SITEMAP_URL]

    sitemap_urls = []

    for sitemap_url in srcs:
        sitemap_urls.extend(get_sitemaps(sitemap_url, sitemap=True))

    links = []

    for sitemap_url in sitemap_urls:
        links.extend(get_sitemaps(sitemap_url))

    df = pd.DataFrame(links)
    df.to_csv("./data/links.csv", index=False, columns=["link"])
