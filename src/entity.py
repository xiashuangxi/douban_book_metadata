#!/usr/bin/evn python

__license__ = 'GPL v3'
__copyright__ = '2023,Xia Shuangxi'

import re
from datetime import datetime


class Author():
    # 标准化处理作者名称。有些作者信息标有国籍信息，如：村上春树(日)，需要转换成
    # 标准化和格式 （日）村上春树。
    def __init__(self, author_string: str):
        self.author = author_string if author_string is not None and 0 < len(
            author_string) else None
        self.regex = ['\((.*?)\)', '\[(.*?)\]',
                      '\【(.*?)\】', '\〔(.*?)\〕', '\（(.*?)\）']

        self.data = self.__make()

    def __make(self):
        if self.author is None:
            return None
        country = None
        for reg in self.regex:
            c = re.findall(reg, self.author)
            if len(c) > 0:
                self.author = re.sub(reg, '', self.author)
                country = c[0]
        return {
            'country': country if country is not None else None,
            'author': self.author
        }

    def __get_country(self):
        return self.data['country']

    def __get_name(self):
        return self.data['author']

    def is_empty(self):
        return False if self.author is not None else True

    def to_string(self):
        c = self.__get_country()
        return self.__get_name() if c is None else '（' + c + '）' + self.__get_name()


class PubDate():
    def __init__(self, arg):
        if arg is not None and len(arg) > 0:
            self.st = arg
        else:
            self.st = datetime.now()

    def to_datetime(self):
        if isinstance(self.st, datetime):
            return self.st
        else:
            if re.compile('^\\d{4}$').match(self.st):
                return datetime.strptime(self.st, '%Y')
            elif re.compile('^\\d{4}-\\d+$').match(self.st):
                return datetime.strptime(self.st, '%Y-%m')
            elif re.compile('^\\d{4}-\\d+-\\d+$').match(self.st):
                return datetime.strptime(self.st, '%Y-%m-%d')


class BookMetaData():
    def __init__(self, id, name, authors, isbn, pages=0, sub_name=None, other_name=None,
                 publisher=None, pubdate=None, translators=None, series=None, rating=None, url=None, img=None, log=None):
        self._id = id
        self._name = name
        self._authors = authors if authors is not None and len(
            authors) > 0 else '-'
        self._isbn = isbn
        self._pages = pages
        self._sub_name = sub_name
        self._other_name = other_name
        self._publisher = publisher
        self._pubdate = pubdate
        self._translators = translators
        self._series = series
        self._rating = rating
        self._url = url
        self._img = img

        self.__check_data()

    def __check_data(self):
        self.__check_id(self._id)
        self.__check_name(self._name)
        self.__check_authors(self._authors)
        self.__check_isbn(self._isbn)

    def __check_id(self, id):
        if self._id is None or len(self._id) == 0:
            raise Exception('书籍的id参数不能是None或空字符串')

    def __check_name(self, name):
        if self._name is None or len(self._name) == 0:
            raise Exception('书籍的name参数不能是None或空字符串')

    def __check_authors(self, authorw):
        if self._authors is None or len(self._authors) == 0:
            raise Exception('书籍的authors参数不能是None或空字符串')

    def __check_isbn(self, isbn):
        if self._isbn is None or len(self._isbn) == 0:
            raise Exception('书籍的isbn参数不能是None或空字符串')

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, id):
        self.__check_id(id)
        self._id = id

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self.__check_name(name)
        self._name = name

    @property
    def authors(self):
        self._authors = self._authors.replace('&', '').split('/')
        for inx, val in enumerate(self._authors):
            self._authors[inx] = Author(val).to_string()
        return self._authors

    @authors.setter
    def authors(self, authors):
        self.__check_authors(authorw)
        self._authors = authors

    @property
    def isbn(self):
        # return self._isbn.replace('-', '')
        return re.sub('\D', '', self._isbn)

    @isbn.setter
    def isbn(self, isbn):
        self.__check_isbn(isbn)
        self._isbn = isbn

    @property
    def pages(self):
        return self._pages

    @pages.setter
    def pages(self, pages):
        self._pages = pages

    @property
    def sub_name(self):
        return self._sub_name

    @sub_name.setter
    def sub_name(self, sub_name):
        self._sub_name = sub_name

    @property
    def other_name(self):
        return self._other_name

    @other_name.setter
    def other_name(self, other_name):
        self._other_name = other_name

    @property
    def publisher(self):
        return self._publisher

    @publisher.setter
    def publisher(self, publisher):
        self._publisher = publisher

    @property
    def pubdate(self):
        return PubDate(self._pubdate).to_datetime()

    @pubdate.setter
    def pubdate(self, pubdate):
        self._pubdate = pubdate

    @property
    def translators(self):
        if self._translators is not None:
            _text = self._translators.split('/')
            _trans = []
            for t in _text:
                _trans.append(t.strip())
                self._translators = ' & '.join(_trans)
        return self._translators

    @translators.setter
    def translators(self, translators):
        self._translators = translators

    @property
    def series(self):
        return self._series

    @series.setter
    def series(self, series):
        self._series = series

    @property
    def rating(self):
        if self._rating is None:
            return 0
        return re.search('([\d]\.[\d])|(\d)', self._rating).group()

    @rating.setter
    def rating(self, rating):
        if rating is not None and len(rating) > 0:
            self._rating = rating
        else:
            self._rating = 0

    @property
    def url(self):
        return self._url

    @url.setter
    def url(self, url):
        self._url = url

    @property
    def img(self):
        return self._img

    @img.setter
    def img(self, img):
        self._img = img

    def preview_authors(self, log=None):
        a = self.authors  # list
        a[-1] = a[-1] + '著'

        if self.translators is not None and len(self.translators) > 0:
            t = self.translators + '译'
            a.append(t)
        return a

    def __str__(self):
        ans = ['BookMetadata:']

        def fmt(x, y):
            ans.append('%-20s: %s' % (str(x).strip(), str(y).strip()))

        fmt('id', self._id)
        fmt('name', self._name)
        fmt('authors', ','.join(self._authors))
        fmt('isbn', self._isbn)
        fmt('pages', str(self._pages))
        fmt('sub_name', self._sub_name)
        fmt('other_name', self._other_name)
        fmt('publisher', self._publisher)
        fmt('pubdate', self._pubdate)
        fmt('translators', self._translators)
        fmt('series', self._series)
        fmt('rating', self._rating)
        fmt('url', self._url)
        fmt('img', self._img)

        return '\n'.join(ans)


class BookNode():
    def __init__(self, id, url, year, pic):
        self.id = id
        self.url = url
        self.year = year
        self.pic = pic

    def __check_data():
        if self.id is None or len(self.id) == 0:
            raise Exception('参数id不存在None或空字符串')
        if self.url is None or len(self.url) == 0:
            raise Exception('参数url不存在None或空字符串')
        if self.year is None or len(self.year) == 0:
            raise Exception('参数year不存在None或空字符串')
        if self.pic is None or len(self.id) == 0:
            raise Exception('参数pic不存在None或空字符串')

    def __str__(self):
        ans = ['BookNode:']

        def fmt(x, y):
            ans.append('%-20s: %s' % (str(x), str(y)))

        fmt('id', self.id)
        fmt('url', self.url)
        fmt('year', self.year)
        fmt('pic', self.pic)

        return '\n'.join(ans)
