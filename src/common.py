import math
import threading


class VersionUpdateException(Exception):
    pass


def conversion_size(size):
    _size = 1024
    _unit = ['B', 'KB', 'MB', 'GB']

    for i in range(1, 5):
        if size < 0.1 * math.pow(_size, i):
            if i == 1:
                return f'{size} {_unit[i-1]}'
            else:
                return f'{round( size / math.pow(_size, i - 1) )} {_unit[i-1]}'
    # if byte < 0.1 * 1024:
    #     print(str(byte)+'B')
    # elif byte < 0.1 * 1024 * 1024:
    #     print(str(byte / 1024)+'KB')
    # elif byte < 0.1 * 1024 * 1024* 1024:
    #     print((byte / (1024* 1024))+'MB')
    # elif byte < 0.1 * 1024 * 1024* 1024* 1024:
    #     print((byte / (1024* 1024* 1024))+'GB')


def is_latest(newv):
    '''
    param: 1.0.0 or v0.2.0-alpha or v5.9-beta.1
    return: 0: 大，-1: 小，0: 相同
    '''
    if newv is None or len(newv) == 0:
        return False
    from calibre_plugins.douban_book_metadata.__init__ import DoubanBookMetadata

    _ov = DoubanBookMetadata.version
    _vd = newv.split('-')
    if len(_vd) == 1:
        _v = _vd[0][1:].split('.')

        _v_old = [int(i) for i in _ov]
        _v_new = [int(i) for i in _v]

        _v_new_len = len(_v_new)
        _v_old_len = len(_v_old)

        if _v_old_len > _v_new_len:
            for i in range(_v_new_len, _v_old_len):
                _v_new.append(0)
        elif _v_new_len > _v_old_len:
            for i in range(_v_old_len, _v_new_len):
                _v_old.append(0)
        print(_v_new, _v_old)
        for i in range(len(_v_new)):
            if _v_new[i] > _v_old[i]:
                return 1
            if _v_new[i] < _v_old[i]:
                return -1
        return 0


class VersionUpdateThread(threading.Thread):

    # def someFunction(self):
    #     name = threading.current_thread().name
    #     raise VersionUpdateException('线程错误：' + name)

    def run(self):
        self.exc = None
        try:
            super().run()
        except BaseException as e:
            self.exc = e

    def join(self):
        threading.Thread.join(self)
        if self.exc:
            raise self.exc
