import logging
import traceback


logging.basicConfig(filemode='douban_book_metadata.log', format='%(asctime)s - %(name)s - %(levelname)s -%(module)s: %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S', level=20)


class Log():

    def _traceback(self):
        return traceback.format_exc()

    @staticmethod
    def info(s):
        logging.info(u'### DBM: {}\n\n {}'.format(s, Log._traceback))

    @staticmethod
    def error(s):
        logging.error(u'### DBM: {}\n\n {}'.format(s, Log._traceback), exc_info=True)

    @staticmethod
    def exception(s, e=None):
        logging.exception(u'### DBM: {}\n\n {}'.format(s, e))
