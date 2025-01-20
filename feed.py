from typing import Dict, List

import feedparser
import pandas as pd
import requests
from bs4 import BeautifulSoup

PUBLIC_URL = "https://www.public.fr/"
VSD_URL = "https://www.vsd.fr/"
HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"
    }

def get_xml_data(url) -> Dict:
    """
    Get XML data from feed URL.
    """
    try:
        response = requests.get(url, headers=HEADERS)
        feed = feedparser.parse(response.content)

        articles = []

        for entry in feed.entries:
            title = entry.title
            link = entry.link
            author = entry.get("author", "N/A")
            published = entry.published
            categories = []
            if "tags" in entry:
                categories = [tag["term"] for tag in entry.get("tags", [])]
            categories = ", ".join(categories)
            description = entry.summary
            # print(f"Title: {title}")
            # print(f"Link: {link}")
            # print(f"Author: {author}")
            # print(f"Published: {published}")
            # print(f"Categories: {categories}")
            # print(f"Description: {description}")
            articles.append(
                {
                    "Title": title,
                    "Link": link,
                    "Author": author,
                    "Published": published,
                    "Categories": categories,
                    "Description": description,
                }
            )
        return articles
    except Exception as e:
        print("Exception Error:", e)
        return {}

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


def get_links(srcs) -> None:
    sitemap_urls = []

    for sitemap_url in srcs:
        sitemap_urls.extend(get_sitemaps(sitemap_url, sitemap=True))

    links = []

    for sitemap_url in sitemap_urls:
        links.extend(get_sitemaps(sitemap_url))

    df = pd.DataFrame(links)
    df.to_csv("links.csv", index=False, columns=["link"])


def get_feeds(url) -> List[str]:
    try:
        print(f"\n\nCurrent URL: {url}")
        response = requests.get(url, headers=HEADERS)
        soup = BeautifulSoup(response.content, "html.parser")

        links_with_title = soup.find_all("a", title=lambda t: t and "articles" in t)

        urls = []
        for a in links_with_title:
            urls.append(a["href"])

        print(urls)
        return urls
    except Exception as e:
        print("Exception Error:", e)
        return []


def get_menu_categories(url) -> List[str]:
    try:
        print(f"\n\nCurrent URL: {url}")
        response = requests.get(url, headers=HEADERS)
        soup = BeautifulSoup(response.content, "html.parser")
        nav_tag = soup.find("nav", id="desktop_menu_header_wrapper")

        menu_categories = []
        for a in nav_tag.find_all("a"):
            menu_categories.append(a["href"])

        return menu_categories
    except Exception as e:
        print("Exception Error:", e)
        return []

if __name__ == "__main__":
    # Get sitemap links
    # public_sitemap_url = "https://public.fr/sitemap_index.xml"
    # vsd_sitemap_url = "https://vsd.fr/sitemap_index.xml"
    # srcs = [public_sitemap_url, vsd_sitemap_url]
    # get_links(srcs)


    # Get feeds
    menu_categories = get_menu_categories(VSD_URL)
    menu_categories.extend(get_menu_categories(PUBLIC_URL))

    # Get all avaiable categoris from public.fr and vsd.fr
    urls = []
    for url in menu_categories:
        urls.extend(get_feeds(url))

    # Get available feed urls
    feeds = []
    for url in urls:
        feeds.extend(get_feeds(url))

    feeds.extend(urls)
    print(f"\n\n feed list: {feeds}")

    # Get feed data
    articles = []
    for url in feeds:
        print(url + "/feed")
        articles.extend(get_xml_data(url + "/feed"))

    df = pd.DataFrame(articles)
    df.to_csv("feeds.csv", index=False)
