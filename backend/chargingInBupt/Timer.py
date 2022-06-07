import datetime
import time


def singleton(cls):
    _instance = {}

    def inner():
        if cls not in _instance:
            _instance[cls] = cls()
        return _instance[cls]
    return inner


@singleton
class Timer(object):
    start_time = 0
    __speed = 60

    def __init__(self):
        self.start_time = datetime.datetime.now()

    def get_cur_timestamp(self):
        return int((datetime.datetime.now().timestamp() - self.start_time.timestamp()) * self.__speed + self.start_time.timestamp())

    def get_cur_format_time(self):
        return datetime.datetime.fromtimestamp(int((datetime.datetime.now().timestamp() - self.start_time.timestamp()) * self.__speed + self.start_time.timestamp())).strftime('%Y-%m-%d %H:%M:%S')


if __name__ == '__main__':
    timer = Timer()
    print(timer.get_cur_timestamp())
    print(timer.get_cur_format_time())
    time.sleep(2)
    print(timer.get_cur_timestamp())
    print(timer.get_cur_format_time())
