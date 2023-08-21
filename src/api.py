#!/usr/bin/evn python

__license__ = 'GPL v3'
__copyright__ = '2023,Xia Shuangxi'

import json
import gzip

from urllib.parse import urlencode
from urllib.request import Request, urlopen

from calibre import random_user_agent

from calibre_plugins.douban_book_metadata.entity import BookNode, BookMetaData
from calibre_plugins.douban_book_metadata.parser import Html


class Helper:
    def __get_headers(self):
        return {
            'User-Agent': random_user_agent(),
            'Accept-Encoding': 'gzip, deflate'
        }

    def request(self, url, log=None):
        response = urlopen(
            Request(url, headers=self.__get_headers(), method='GET'))

        if response.info().get('Content-Encoding') == 'gzip':
            data = gzip.decompress(response.read())
        else:
            data = response.read().decode(
                response.headers.get_content_charset())
        return data


def get_books(t, log=None):
    books = []
    url = 'https://book.douban.com/j/subject_suggest?' + urlencode(
        {'q': t})
    data = json.loads(Helper().request(url))
    for node in data:
        books.append(BookNode(
            node.get('id'),
            node.get('url'),
            node.get('year'),
            node.get('pic')
        ))
    return books if len(books) > 0 else None


def get_book_meta(id: str, log=None):
    url = 'https://book.douban.com/subject/%s/' % id
    data = Html().parse(Helper().request(url), log)

    return BookMetaData(
        str(id),
        data.get('name'),
        data.get('作者'),
        data.get('ISBN'),
        data.get('页数'),
        data.get('副标题'),
        data.get('原作名'),
        data.get('出版社'),
        data.get('出版年'),
        data.get('译者'),
        data.get('丛书'),
        data.get('rating'),
        url,
        None,
        log=log
    )
