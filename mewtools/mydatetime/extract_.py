import re
import time
import maya

from datetime import datetime
from datetime import timedelta
from dateutil import parser
from date_extractor import extract_dates
from mylibtool.mydatetime import timezone

timestamp_reg = re.compile(r"^(\d{10,})$|"  # 10位时间戳
                           r"^(\d{13,})$|"  # 13位时间戳
                           r"^(\d{10,}\.\d{1,7})$")  # 这种形式只匹配最近的时间戳，由1开始，列如 1654280040

direct_pattern = re.compile(r"^(\d{10,})$|"  # 10位时间戳
                            r"^(\d{13,})$|"  # 13位时间戳
                            r"^(1\d{9,}\.\d{1,3})$|"  # 这种形式只匹配最近的时间戳，由1开始，列如 1654280040
                            r"^(\d{4}-\d{2}-\d+)$|"
                            r"^(\d{4}-\d{2}-\d+ \d{2})$|"
                            r"^(\d{4}-\d{2}-\d+ \d{2}:\d{2})$|"
                            r"^(\d{4}-\d{2}-\d+ \d{2}:\d{2}:\d{2})$")


def check_format(text):
    text_termed = replace_comma(text)

    if direct_pattern.search(text_termed):
        print('match')


def replace_comma(text):
    """Comma filter"""
    commas = {
        "年": "-",
        "月": "-",
        "日": " ",
        "时": ":",
        "分": ":",
        "秒": " ",
        "(": " ",
        ")": " ",
    }
    rs = map(lambda x: commas[x] if x in commas.keys() else x, list(text))
    return "".join(list(rs))


def replace_tzinfo(text):
    # 替换成偏移量
    pass


def is_pure_datetime(text):
    rule = re.compile(r"^[\d.,: at|Sun|Mon|Tue|Wed|Thu|Fri|Sat|January|-]+$")
    if rule.search(text):
        return True


def get_datetime(text):
    """Convert or extract datetime"""
    the_datetime = directly_datetime(text)
    if the_datetime:
        # 直接转换时间
        return the_datetime
    else:
        # 从文本抽取时间
        return extract(text)


def extract(text):
    date_tmp = extract_dates(text)
    if date_tmp:
        return date_tmp[0]


def directly_datetime(text):
    """
    用两种方法来转换直接的时间字符串
    :param text:
    :return:
    """
    if len(text) > 50:
        # 太长的不可能时直接时间
        return False

    # 判断是否时间戳
    if timestamp_reg.search(text):
        if re.search(r'^\d+$', text):
            # 不带小数点的13位时间戳转换位10位
            text = text[:10]

        ts = int(float(text))
        return maya.MayaDT(ts).datetime()

    text = replace_comma(text)  # 替换中文等干扰

    timezones_dic = timezone.timezones_dic
    the_datetime = None
    maya_datetime = None
    dateutil_datetime = None

    try:
        maya_tmp = maya.parse(text)
        if maya_tmp.epoch < 0:
            # Convert if date earlier than 1970
            maya_datetime = datetime(1970, 1, 1) - timedelta(seconds=abs(maya_tmp.epoch))
        else:
            maya_datetime = maya_tmp.datetime()
    except:
        pass

    try:
        dateutil_datetime = parser.parse(text, tzinfos=timezones_dic)
    except:
        pass

    if dateutil_datetime and maya_datetime and dateutil_datetime.tzinfo:
        # 将 dateutil拿到的时区写到 maya拿到的时间
        maya_datetime = maya_datetime.replace(tzinfo=dateutil_datetime.tzinfo)

    return maya_datetime


if __name__ == '__main__':
    time_list = [
        "1994-02-21T12:00:00+05:30",
        '1507150827',
        '1607150827.111',
        '1607150827111',
        '1970年01月01日3时00分00秒',
        '1970年01月01日',
        '1/2/2000',
        '01/02/2000',
        '31/01/2000T',
        '31/1/2000',
        '01/30/2000',
        '29-02-2000',
        '29/Mar/2020',
        '29/Mar/22',
        '8 Aug 2020',
        'Dec-01-2000',
        '2020.1.29',
        '2020.01.29',
        '2020.1.8 2:30',
        '2020.1.8 02:30:01',
        '2020.1.8 02:30:01.000',
        '2020.1.8 2am',
        '2020.1.8 2pm',
        '10 Jan. 1896',
        'Jan.26 1896',
        '2016-08-9T10:01:54.123Z ',
        '20160809',
        '1896-10-30',
        'Jan 2009',
        '1992/02/12 12:23:22+0800',
        '2016-08-06 8:00PM CST',
        '2016-08-06 08:00PM Z',
        'Jinstin said at 2020-10-30',
    ]
    for item in time_list:
        # t = get_datetime(item)
        t = directly_datetime(item)
        print(t)
