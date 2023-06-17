import json

import source.connect
from mongoengine import disconnect
from mongoengine.queryset import DoesNotExist
from source.models import Authors, Quotes

from typing import List, Dict


def read_authors(authors_json_file: str) -> List[Dict]:
    """
    Зчитування даних про авторів з JSON-файлу.

    :param authors_json_file: Шлях до JSON-файлу з даними про авторів.
    :return: Список словників з даними про авторів.
    """
    with open(authors_json_file, 'r', encoding='utf-8') as fd:
        result = json.load(fd)
    return result


def read_quotes(quotes_json_file: str) -> List[Dict]:
    """
    Зчитування даних про цитати з JSON-файлу.

    :param quotes_json_file: Шлях до JSON-файлу з даними про цитати.
    :return: Список словників з даними про цитати.
    """
    with open(quotes_json_file, 'r', encoding='utf-8') as fd:
        result = json.load(fd)
    return result


def seed_authors():

    """Наповнення БД даними про автора."""

    Authors.objects().delete()
    authors = read_authors('authors.json')
    for author in authors:
        Authors(
            full_name=author.get('author_fullname'),
            born_date=author.get('author_bday'),
            born_loc=author.get('author_born_loc'),
            desc=author.get('author_desc')
        ).save()


def seed_quotes():

    """Наповнення БД інформацією цитат."""

    Quotes.objects().delete()
    quotes = read_quotes('quotes.json')
    for quote in quotes:
        try:
            Quotes(
                tags=quote.get('tags'),
                author=Authors.objects.get(full_name=quote.get('author')),
                quote=quote.get('text'),
            ).save()
        except DoesNotExist:
            Quotes(
                tags=quote.get('tags'),
                author=None,
                quote=quote.get('text'),
            ).save()


if __name__ == "__main__":
    seed_authors()
    seed_quotes()
    disconnect()
