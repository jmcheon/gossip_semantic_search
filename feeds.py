from typing import Dict, List

import feedparser
import pandas as pd
import requests
from bs4 import BeautifulSoup

PUBLIC_URL = "https://www.public.fr/"
VSD_URL = "https://www.vsd.fr/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
    + " Chrome/112.0.0.0 Safari/537.36"
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
            # content = entry.get("content", [{}])[0].get("value", "N/A")
            # plain_content = BeautifulSoup(content, "html.parser").get_text()
            # print(f"Title: {title}")
            # print(f"Link: {link}")
            # print(f"Author: {author}")
            # print(f"Published: {published}")
            # print(f"Categories: {categories}")
            # print(f"Description: {description}")
            # print(f"Content: {plain_content}")
            articles.append(
                {
                    "Title": title,
                    "Link": link,
                    "Author": author,
                    "Published": published,
                    "Categories": categories,
                    "Description": description,
                    # "Content": plain_content,
                }
            )
        return articles
    except Exception as e:
        print("Exception Error:", e)
        return {}


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
        print("Processing feed: ", url + "/feed")
        articles.extend(get_xml_data(url + "/feed"))

    df = pd.DataFrame(articles)
    df.to_csv("./data/feeds.csv", index=False)
