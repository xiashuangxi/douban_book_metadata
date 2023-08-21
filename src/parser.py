#!/usr/bin/evn python

__license__ = 'GPL v3'
__copyright__ = '2023,Xia Shuangxi'

import re
from lxml import etree


class Html():
    def __init__(self):
        self.html = None
        self.book_info = {}

    def __get_text(self, el):
        text = None
        if el is not None and len(el) > 0 and el[0].text:
            text = el[0].text.strip()
        elif isinstance(el, etree._Element) and el.text:
            text = el.text.strip()
        return text if text else None

    def __get_rating(self):
        el = self.html.xpath('//strong[@property="v:average"]')
        return self.__get_text(el)

    def __get_name(self):
        el = self.html.xpath('//span[@property="v:itemreviewed"]')
        return self.__get_text(el)

    def __make_info(self, log=None):
        els = self.html.xpath('//div[@id="info"]')

        info = els[0].xpath('string(.)') if len(els) > 0 else None

        if info is not None:
            info = re.sub('(\\n\\n)', '|', info)
            info = re.sub('(\\n)', '', info)
            info = info.split('|')

            info = [i for i in info if len(i.strip()) > 0]

            for i in info:
                if log:
                    log.info(i)
                key, value = i.split(':', 1)
                self.book_info[key.strip()] = value.strip()

    def parse(self, html, log=None):
        if html is None or len(html) == 0:
            return None
        self.html = etree.HTML(html)

        self.book_info['name'] = self.__get_name()
        self.book_info['rating'] = self.__get_rating()
        self.__make_info(log)
        return self.book_info
