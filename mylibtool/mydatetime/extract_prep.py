"""提取 datetime 前对文本的调整"""
import re
import datetime
from loguru import logger
from mylibtool.mydatetime import month_pair


def _filter_middle_part(text):
    """过滤日期与时间部分的干扰"""
    if re.search(r'\d{1,2} at \d{1,2}', text):
        text = text.replace(' at ', ' ')

    return text


def format2year_month_day(text, day_first):
    """格式化非标准的日期为 yy-mm-dd 格式"""
    text = f' {text} '  # 前后加空格，防止首尾为^或$

    text = _replace_named_month(text)  # 把英文月份转换成数字月份

    '''↓ mm/dd/yy | dd/mm/yy 格式处理开始 ↓'''

    def _to_ymd(matched):
        non_ymd_list = list(matched.groups())
        if day_first:
            # 默认遵循月份在前，所以 dayfirst 的情况需要交换两个的位置
            non_ymd_list[0], non_ymd_list[2] = non_ymd_list[2], non_ymd_list[0]

        # 判断 date 有效性，并尝试更正，无法更正就让 extract 无效
        try:
            non_ymd_list = _to_ymd_check_valid(non_ymd_list)
        except Exception as e:
            logger.warning(e)
            return 'Date Invalid'

        ymd_str = f'{non_ymd_list[3]}-{non_ymd_list[0]}-{non_ymd_list[2]} {non_ymd_list[-1]}'
        return ymd_str

    text = re.sub(r'(\d{1,2})([ /.·-]+)(\d{1,2})\2(\d{4})[^\d](\d{1,2}:\d{2})', _to_ymd, text)
    '''↑ mm/dd/yy | dd/mm/yy 格式处理结束 ↑'''

    '''↓ yy-mm-dd 格式处理开始 ↓'''
    text = re.sub(r'\D([12]\d{3})([/.·-]+)(\d)\2(\d{2})\D', r' \1-0\3-\4 ', text)  # 修改 单位数月份为双位数
    text = re.sub(r'\D([12]\d{3})([/.·-]+)(\d{2})\2(\d)\D', r' \1-\3-0\4 ', text)  # 修改 单位数日期为双位数

    text = re.sub(r'([12]\d{3})([ /.·]+)(\d{2})\2(\d{2})\D', r'\1-\3-\4 ', text)  # 修改其他日期分隔符为-

    text = _filter_middle_part(text)  # 过滤日期和时间中间的干扰

    time_reg = re.compile(r'(\d{4}-\d{2}-\d{2}) {1,2}([0-2]?\d(:[0-6]\d){1,2})( ?am| ?pm| ?a.m.| ?p.m.|[^:\d])', re.I)  # 第一组为日期，第二组为时间，第三组为 am 或 pm
    text = re.sub(time_reg, _final_time_callback, text)  # 修改 单位数小时为双位，补全秒

    text = re.sub(r'(\D)(\d{4}-\d{2}-\d{2} [0-2]\d:[0-6]\d)', r';\2', text)  # 日期前面有数字会影响提取，此处用分隔符隔开，如 0.105 2021-04-01 to 0.105;2021-04-01
    '''↑ yy-mm-dd 格式处理结束 ↑'''

    return text


def _replace_named_month(text):
    """英文月份转换为数字月份，并且转化为 （年-月-日） 形式"""
    reg1 = re.compile(r'(?<=[^a-zA-Z])(January|February|March|April|May|June|July|August|September|October|November|December)(?=[/.,\d -]+)', re.I)  # 匹配月份全称
    step1_text = re.sub(reg1, _month_callback, text)  # 月份转换后用 '龘' 作为识别符

    reg1 = re.compile(r'(?<=[^a-zA-Z])(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\.?(?=[/.,\d -]+)', re.I)  # 匹配月份简写，可以匹配 Jan. 这样的简写。 https://regexr.com/6n41e
    step1_text = re.sub(reg1, _month_callback, step1_text)  # 月份转换后用 '龘' 作为识别符

    '''↓用非逗号和逗号分割月 日, 年的情况↓'''
    step1_text = re.sub(r'(\d{1,2}龘)[ .](\d{1,2}), ?(\d{4})', r'\1/\2/\3', step1_text)
    '''↑用非逗号和逗号分割月 日, 年的情况↑'''

    # 月份在中间的情况
    reg2 = re.compile(r'(\d{4}|\d{1,2})([ /.·-]+)(\d{2}龘)\2(\d{4}|\d{1,2})[\D]')  # 英文名月份很可能由空格分割
    step2_text = re.sub(reg2, _sort_ymd_by_mark_callback, step1_text)

    # 月份在前的情况
    reg3 = re.compile(r'(\d{2}龘)([ /.·-]+)(\d{4}|\d{1,2})\2(\d{4}|\d{1,2})[^:\d]')  # 英文名月份很可能由空格分割
    step3_text = re.sub(reg3, _sort_ymd_by_mark_callback, step2_text)

    return step3_text


def _sort_ymd_by_mark_callback(matched):
    """排序 yy-mm-dd，月份使用 龘 修饰的情况"""
    ymd_list = matched.groups()

    year = ''
    month = ''
    day = ''

    # 获取年月日
    for m in ymd_list:
        if len(m) == 4 and m.isdigit():
            year = m
        elif '龘' in m:
            month = m.replace('龘', '')
        elif len(m) <= 2 and m.isdigit():
            day = m

    return f'{year}-{month}-{day} '


def _month_callback(matched):
    """正则取英文月份，用（双位数字+龘）来替换成对应月份"""
    symbol = matched.group(1)
    if not symbol:
        return symbol

    if not symbol[0].isupper():
        # 首字母为小写，可能不是日期
        return symbol

    for m in month_pair.month_map:
        if m[0] == symbol.title() or m[1] == symbol.title():
            month_instead = m[2] + "龘"
            return month_instead


def _final_time_callback(matched):
    """对时间进行最终的调整，修改 单位数小时为双位，补全秒"""
    t_list = matched.groups()

    t_nums = t_list[1].split(':')  # 分割时间为数字

    def __include(str_list, *args):
        for k in args:
            for t in str_list:
                if k == t.lower():
                    return True

    if __include(t_list, 'am', ' am', ' a.m.', 'a.m.'):
        # 补全单位数的小时（上午）
        if len(t_nums[0]) == 1:
            t_nums[0] = f'0{t_nums[0]}'
    elif __include(t_list, 'pm', ' pm', ' p.m.', 'p.m.'):
        # 补全单位数的小时（下午）
        if int(t_nums[0]) < 12:
            pm_hour = str(int(t_nums[0]) + 12)
            t_nums[0] = pm_hour
    elif len(t_nums[0]) == 1:
        # 没有 am,pm 标识，但是时间为1位数
        t_nums[0] = f'0{t_nums[0]}'

    # 补全秒数
    if len(t_nums) == 2:
        t_nums.append('00')

    return f'{t_list[0]} {":".join(t_nums)}'


def _get_days(year, month):
    """获取特定月份的天数"""
    if month in (1, 3, 5, 7, 8, 10, 12):
        return 31
    elif month in (4, 6, 9, 11):
        return 30
    elif month == 2:
        if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0):
            return 29
        else:
            return 28
    else:
        raise Exception("Year Invalid")


def _to_ymd_check_valid(non_ymd_list):
    """
    判断 date 有效性，尝试更正
    返回更正后的 list, 若更正失败则触发异常
    """
    year = int(non_ymd_list[3])  # 年
    month = int(non_ymd_list[0])  # 月
    day = int(non_ymd_list[2])  # 日
    if (month > 12) and (day < 13):
        # 月大于12，但是日小于12，那么月和日应该是反了
        non_ymd_list[0], non_ymd_list[2] = non_ymd_list[2], non_ymd_list[0]
        # 月、日重新取值
        month = int(non_ymd_list[0])
        day = int(non_ymd_list[2])

    # 日期超过该月合理天数则无效
    if day > _get_days(int(year), int(month)):
        raise Exception("Day Invalid")

    # 月份有效判断
    if month > 12:
        raise Exception("Month Invalid")

    # 年有效判断
    if year > 2050:
        raise Exception("Year over 2050")

    return non_ymd_list


def timez_str_convert(text):
    """text 中时间字符串转换成偏移格式"""
    text = re.sub(r'(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2}):(\d{2}) GMT([+-])([:\d]+)', _gmt2offset, text)
    return text


def _datetime_math(time_list, offset_symbol, offset_h, offset_m):
    """datetime 加减"""
    the_datetime = datetime.datetime.now().replace(
        year=time_list['yy'],
        month=time_list['mm'],
        day=time_list['dd'],
        hour=time_list['h'],
        minute=time_list['m'],
        second=time_list['s'],
        microsecond=0
    )  # 用 string 转成 datetime

    if offset_symbol == '-':
        modified_datetime = the_datetime + datetime.timedelta(minutes=offset_m)
        modified_datetime = modified_datetime + datetime.timedelta(hours=offset_h)
    else:
        modified_datetime = the_datetime - datetime.timedelta(minutes=offset_m)
        modified_datetime = modified_datetime - datetime.timedelta(hours=offset_h)

    return modified_datetime


def _gmt2offset(matched):
    t_list = matched.groups()

    # 年、月、日、时、分
    time_list = {
        'yy': int(t_list[0]),
        'mm': int(t_list[1]),
        'dd': int(t_list[2]),
        'h': int(t_list[3]),
        'm': int(t_list[4]),
        's': int(t_list[5]),
    }
    offset_symbol = t_list[-2]  # 正负符号

    if len(t_list[-1]) == 1:
        # 偏移只有小时位，偏移小时和偏移分钟
        offset_h = int(t_list[-1])
        offset_m = 0
    else:
        # 偏移有小时位和分钟位
        if ':' in t_list[-1]:
            hm = t_list[-1].split(':')
            offset_h = int(hm[0])
            offset_m = int(hm[1])
        else:
            offset_h = int(t_list[-1][0:1])
            offset_m = int(t_list[-1][2:3])

    modified_datetime = _datetime_math(time_list, offset_symbol, offset_h, offset_m)

    modified_datetime_str = f'{modified_datetime.strftime("%Y-%m-%d %H:%M:%S")}{offset_symbol}{str(offset_h).zfill(2)}{str(offset_m).zfill(2)}'

    return modified_datetime_str

