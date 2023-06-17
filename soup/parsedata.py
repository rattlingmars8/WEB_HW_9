import json
import logging
import time
from multiprocessing import Pool

import aiohttp
import asyncio
from bs4 import BeautifulSoup
from typing import List, Dict, Any

base_url = "https://quotes.toscrape.com"
author_links = set()


def setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
    )


def parse_quotes_in_page(html_doc: str) -> List[Dict[str, Any]]:
    """
    Парсинг цитат з HTML-документа.

    :param html_doc: HTML-документ
    :return: список цитат
    """
    quotes = []

    soup = BeautifulSoup(html_doc, "lxml")
    quote_elements = soup.select(".quote")
    for quote_element in quote_elements:
        text = quote_element.find("span", attrs={"class": "text"}).text
        author = quote_element.find("small", attrs={"class": "author"}).text
        tags = [tag.text for tag in quote_element.find_all("a", attrs={"class": "tag"})]
        author_href = (
                f"http://quotes.toscrape.com" + quote_element.select_one("a")["href"]
        )
        author_links.add(author_href)
        quotes.append({"text": text, "author": author, "tags": tags})
    return quotes


async def handle_pagination_async(session: aiohttp.ClientSession) -> Any:
    """
    Асинхронна обробка пагінації.

    :param session: aiohttp.ClientSession
    :return: генератор з URL та HTML-документом
    """
    page: int = 1
    while True:
        if page == 1:
            url: str = base_url
        else:
            url = f"{base_url}/page/{page}"
        async with session.get(url) as response:
            if response.status != 200:
                break
            html_doc: str = await response.text()
            yield url, html_doc  # Повертаємо url та HTML-сторінку у текстовомову виляді
            page += 1


def parse_data_author(html_doc: str) -> List[Dict[str, Any]]:
    """
    Парсинг даних про автора з HTML-документа.

    :param html_doc: HTML-документ
    :return: список авторів
    """
    authors = []
    soup = BeautifulSoup(html_doc, "lxml")
    author_details = soup.select_one(".author-details")
    if author_details:
        author_fullname: str = author_details.find(
            "h3", attrs={"class": "author-title"}
        ).text.strip()
        author_bday: str = author_details.find(
            "span", attrs={"class": "author-born-date"}
        ).text.strip()
        author_born_loc: str = author_details.find(
            "span", attrs={"class": "author-born-location"}
        ).text.strip()
        author_desc: str = author_details.find(
            "div", attrs={"class": "author-description"}
        ).text.strip()
        authors.append(
            {
                "author_fullname": author_fullname,
                "author_bday": author_bday,
                "author_born_loc": author_born_loc,
                "author_desc": author_desc,
            }
        )
    return authors


async def parse_all_quotes_async() -> List[Dict[str, Any]]:
    """
    Асинхронний парсинг всіх цитат.

    :return: список цитат
    """
    result = []
    async with aiohttp.ClientSession() as session:
        async for url, page_text in handle_pagination_async(session):
            quotes = parse_quotes_in_page(page_text)
            if not quotes:
                break
            result.extend(quotes)
            logging.info(f"Page parsed: {url}")
        logging.info(f"\n\nTotal parsed - {len(result)} quotes.\n\n")
    return result


async def parse_all_author_data_async(url: str, session: aiohttp.ClientSession) -> List[Dict[str, Any]]:
    async with session.get(url) as response:
        html_doc = await response.text()
        authors = parse_data_author(html_doc)
        logging.info(f"Author parsed: {url}")
        return authors


async def parse_all_authors_async(urls: List[str]) -> List[Dict[str, Any]]:
    async with aiohttp.ClientSession() as session:
        tasks = []
        for url in urls:
            task = parse_all_author_data_async(url, session)
            tasks.append(task)
        authors_list = await asyncio.gather(*tasks)
        authors = [author for sublist in authors_list for author in sublist]
        logging.info(f"\n\nTotal parsed - {len(authors)} authors.\n\n")
        return authors


async def main_async() -> None:
    setup_logging()
    start_time = time.time()
    all_quotes = await parse_all_quotes_async()

    # Парсимо дані про авторів за допомогою асинхронності
    all_authors = await parse_all_authors_async(author_links)

    end_time = time.time()
    execution_time = end_time - start_time

    with open("quotes.json", "w", encoding="utf-8") as file:
        json.dump(all_quotes, file, indent=4, ensure_ascii=False)
    logging.info(f"Saving QUOTES to 'quotes.json' file...")

    with open("authors.json", "w", encoding="utf-8") as file:
        json.dump(all_authors, file, indent=4, ensure_ascii=False)
    logging.info(f"Saving AUTHORS to 'authors.json' file...")

    logging.info(f"Execution time: {execution_time} seconds")


if __name__ == "__main__":
    asyncio.run(main_async())
