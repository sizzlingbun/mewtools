import re
import maya
import warnings

from datetime import datetime
from datetime import timedelta
from dateutil import parser
from date_extractor import extract_dates
from mylibtool.mydatetime import timezone
from mylibtool.mydatetime import month_pair
from mylibtool.mydatetime import extract_prep


timestamp_reg = re.compile(r"^(\d{10,})$|"  # 10位时间戳
                           r"^(\d{13,})$|"  # 13位时间戳
                           r"^(\d{10,}\.\d{1,7})$")  # 这种形式只匹配最近的时间戳，由1开始，列如 1654280040


def replace_comma(text):
    """清除常见干扰"""
    text = re.sub(r'日\D', r'日', text)  # 去掉 日后面的非数字干扰，列如：2022年7月12日T20:50:00

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


def extract(text, day_first, method='date'):
    """
    从文本提取 datetime, 只有 date_extractor 库有提取功能
    extract_dates 函数提取日期默认是月份在前，列如：04-10-2013 提取为 2013-04-10
    :param text:
    :param method: 提取日期+时间还是只提取日期
    :param day_first: 字符串里，日期在前，默认则是月份在前
    :return:
    """
    if method == 'datetime':
        # 提取日期+时间
        text = replace_comma(text)
        text = _term_day(text)

        formatted_text = extract_prep.format2year_month_day(text, day_first)

        # 经过以上多重过滤后，先尝试使用 directly_datetime 来转换
        # try_directly_datetime = str2datetime(text, None, day_first)
        # if try_directly_datetime:
        #     print(f'-- {try_directly_datetime}')
        # else:
        #     formatted_text = extract_prep.timez_str_convert(formatted_text)

        date_tmp = extract_dates(formatted_text)
        if date_tmp:
            return date_tmp[0]

    else:
        # 只提取日期
        text = replace_comma(text)
        text = _term_day(text)

        if day_first:
            # day 在前需要调换顺序
            text = _interchange_month_day(text)

        date_tmp = extract_dates(text)
        if date_tmp:
            return date_tmp[0]


def _interchange_month_day(text):
    """
    因为 date_extractor 只能解析月份在前的格式
    所以日期在前的 text 必须先交换日和月的位置才能被 date_extractor 解析
    """
    interchanged_text = re.sub(r'(0?[1-9]|[12][0-9]|3[01])[/.](0?[1-9]|1[012])[/.](\d{4})', r'\2/\1/\3', text)
    return interchanged_text


def _term_day(text):
    """
    修剪日期，将 1st, 2nd, 3rd, 4th-9th 精简为双位数字
    """
    termed_text = re.sub(r'(\d)(st|nd|rd|th)', r'0\1', text)
    return termed_text


def str2datetime(text, custom_timezones, day_first):
    """
    用 dateutil 和 maya 库转换直接的时间字符串成 datetime
    :param custom_timezones: 自定义时区偏移字典，用来覆盖 timezone.py 里面的数据，列如 timezones_dic = {"CST": 8 * 3600}
    :param text:
    :return:
    """
    if len(text) > 50:
        # 太长的不可能是直接时间
        return False

    if custom_timezones and not isinstance(custom_timezones, dict):
        raise Exception('custom_timezones must be a dict')

    if timestamp_reg.search(text):
        # 直接转换时间戳为 datetime
        if re.search(r'^\d+$', text):
            # 不带小数点的13位时间戳转换位10位
            text = text[:10]

        ts = int(float(text))
        return maya.MayaDT(ts).datetime()

    # 以下处理非时间戳的字符串
    text = replace_comma(text)  # 替换中文等干扰

    timezones_dic = timezone.timezones_dic
    maya_datetime = None
    dateutil_datetime = None

    """使用 maya 库转换时间"""
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")  # 忽略警告

            maya_tmp = maya.parse(text, day_first=day_first)
            if maya_tmp.epoch < 0:
                # maya 不能转换 1970以前的 datetime，所以这样处理
                maya_datetime = datetime(1970, 1, 1) - timedelta(seconds=abs(maya_tmp.epoch))
            else:
                maya_datetime = maya_tmp.datetime()
    except:
        pass

    """使用 dateutil 库转换时间"""
    try:
        if custom_timezones:
            # 用自定义的时区偏移替换通用的时区偏移
            timezones_dic.update(custom_timezones)

        dateutil_datetime = parser.parse(text, tzinfos=timezones_dic, dayfirst=day_first)
    except:
        pass

    """融合结果，这样会更准确"""
    if dateutil_datetime and maya_datetime and dateutil_datetime.tzinfo:

        # 将 dateutil 拿到的时区融合到 maya 的 datetime
        maya_datetime = maya_datetime.replace(tzinfo=dateutil_datetime.tzinfo)

        # maya 库会把(12:00:00+06:00) 格式的时间转化为 UTC 时间，这会相差 tzinfo 个时间，所以需要 ±tzinfo 调整回来
        matched = re.search(r'\D(\d{2}:\d{2}(\.\d{3,6})?([+-])\d{2}:?\d{2})($|\D)', text)
        if matched:
            # 获取相对于 UTC 的时间差
            offset_tmp = str(maya_datetime.tzinfo)
            try:
                offset_seconds = int(offset_tmp.replace(')', '').split(',')[1])
                maya_datetime = maya_datetime + timedelta(seconds=offset_seconds)
            except:
                pass

    return maya_datetime



