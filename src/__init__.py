#!/usr/bin/evn python

__license__ = 'GPL v3'
__copyright__ = '2023,Xia Shuangxi'

import re

from queue import Queue, Empty

from calibre.ebooks.metadata import check_isbn
from calibre.ebooks.metadata.book.base import Metadata
from calibre.ebooks.metadata.sources.base import Source
# , Option

import calibre_plugins.douban_book_metadata.api as api
from calibre_plugins.douban_book_metadata.config import prefs

__PROGRAM_ID__ = 'douban_book_metadata'


class DoubanBookMetadata(Source):

    name = '豆瓣图书元数据'
    description = '获取豆瓣图书元数据'
    supported_platforms = ['windows', 'osx', 'linux']
    author = 'Xia Shuangxi'
    version = (1, 0, 0)
    minimum_calibre_version = (0, 7, 53)
    capabilities = frozenset(['identify', 'cover'])
    touched_fields = frozenset([
        'title',
        'authors',
        'series',
        'publisher',
        'pubdate',
        'rating',
        'identifier:isbn',
        'identifier:other_name',
        'identifier:douban_url',
        'identifier:translators',
        'identifier:douban_rating',
        'identifier:' + __PROGRAM_ID__,
        'identifier:pages'
    ])

    # options = (
    #     Option(
    #         'douban_bookname_extend_format', 'string', '{出版年份} - {书名}',
    #         '在书名中显示出版年份：',
    #         '在书名中显示出版的年份，可以有效的避免同书名、同作者不同版次的书显示不全。显示格式默认是：{出版年份} - {书名}'
    #     ),
    # )

    def __init__(self, *args, **kwargs):
        Source.__init__(self, *args, **kwargs)

    def identify(
            self,
            log,
            result_queue,
            abort,
            title=None,
            authors=None,
            identifiers={},
            timeout=30):

        isbn = check_isbn(identifiers.get('isbn', None))
        books = api.get_books(isbn or title, log)

        if books is not None and len(books):
            metas = []

            # log.info('==============================================')
            # log.info('查询到 %s 本书' % len(books))
            for book in books:
                b_meta = api.get_book_meta(book.id, log)
                b_meta.img = book.pic
                metas.append(b_meta)
            # log.info('==============================================')

            for meta in metas:
                meta = self.make_metadata(meta, log)
                if isinstance(meta, Metadata):
                    __id = meta.identifiers[__PROGRAM_ID__]
                    if meta.isbn:
                        self.cache_isbn_to_identifier(meta.isbn, __id)
                    if meta.cover:
                        self.cache_identifier_to_cover_url(
                            __id, meta.cover)
                    self.clean_downloaded_metadata(meta)
                    result_queue.put(meta)

    def get_cover_url(self, identifiers, log=None):
        url = None
        __id = identifiers.get(__PROGRAM_ID__, None)
        if __id is None:
            isbn = check_isbn(identifiers.get('isbn', None))
            if isbn is not None:
                __id = self.cached_isbn_to_identifier(isbn)
        if __id is not None:
            url = self.cached_identifier_to_cover_url(__id)

        return url

    def get_book_url(self, identifiers):
        __id = identifiers.get(__PROGRAM_ID__, None)
        if __id is not None:
            return (__PROGRAM_ID__, __id, 'https://book.douban.com/subject/%s/' % __id)

    def download_cover(
            self,
            log,
            result_queue,
            abort,
            title=None,
            authors=None,
            identifiers={},
            timeout=30,
            get_best_cover=False):

        url = self.get_cover_url(identifiers, log)

        if url is None:
            rq = Queue()

            self.identify(log, rq, abort, title=title,
                          authors=authors, identifiers=identifiers)

            if abort.is_set():
                return

            results = []
            while True:
                try:
                    results.append(rq.get_nowait())
                except Empty:
                    break
            results.sort(
                key=self.identify_results_keygen(
                    title=title, authors=authors, identifiers=identifiers
                )
            )
            for mi in results:
                url = self.get_cover_url(identifiers)
                if url is not None:
                    break
        if url is None:
            return

        log.info("封面：" + url)

        browser = self.browser
        browser = browser.clone_browser()
        data = browser.open_novisit(url).read()
        if data:
            result_queue.put((self, data))

    def make_metadata(self, book, log=None):
        if book:
            name = book.name
            if book.sub_name is not None and len(book.sub_name) > 0:
                name = name + ': ' + book.sub_name

            name_exend = prefs.get(
                'douban_bookname_extend_format')

            if name_exend is not None and len(name_exend.strip()) > 0:
                _name = re.sub(
                    '{出版年份}', book.pubdate.strftime('%Y'), name_exend)
                _name = re.sub('{书名}', name, _name)
                name = _name

            meta = Metadata(name, book.preview_authors(log))
            meta.identifiers = {
                __PROGRAM_ID__: book.id,
                'other_name': book.other_name,
                # 'douban_url': book.url,
                # 'douban_img': book.img,
                'translators': book.translators,
                'douban_rating': book.rating,
                'pages': book.pages
            }
            meta.url = book.url
            meta.cover = book.img
            meta.has_cached_cover_url = True
            meta.publisher = book.publisher
            meta.pubdate = book.pubdate
            meta.isbn = book.isbn
            meta.series = book.series
            return meta

    def config_widget(self):
        # try:
        # from calibre.gui2.metadata.config import ConfigWidget
        from calibre_plugins.douban_book_metadata.config import ConfigWidget
        # return ConfigWidget(self)
        return ConfigWidget()
        # except: pass
