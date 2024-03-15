from mylibtool import mydatetime

if __name__ == '__main__':
    time_list = [
        'Dec-11-1987T12:00:00 GMT+8',
        'January 4th, 2017 at 8:00pm',
        # "1994-02-21T23:00:00+10:30",
        # '1992/02/12 12:23:22+0900',
        # '2016-08-06 8:00PM CST',
        # '2016-08-06 8:00PM GET',
        # '2016-08-06 08:00PM Z',
        # '1507150827',
        # '1607150827.111',
        # '1607150827111',
        # '1970年01月01日3时00分00秒',
        # '1970年01月01日',
        '1/2/2000 12:23:22+0900',
        '01/02/2000',
        '31/01/2000T12:23:22+09:00',
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
        # 'Jinstin said at 2020-10-30',
    ]

    # for item in time_list:
    #     # t = get_datetime(item)
    #     t = mydatetime.directly_datetime(item)
    #     print(t)

    text_list = [
        # 'ELIZA STRICKLAND 14 JUL 2022 10 MIN READ',
        # '2018-01-01 10:00:00',
        # '08-24-01',
        # '6/12/1958',
        # '29/02/2000',
        # '04-10-2013',
        # '01/Oct/2000',
        # '2022-06-28T09:30:00',
        # 'created 01/15/2005 by ACME Inc. and associates.',
        # 'Saturday, 09 July 2022 09:41:21 PM',
        # '07/08/2022 04:55 PM EDT',
        # 'Jul. 9, 2022 at 5:07 PM GMT+8',
        # 'July 8, 2022 4:11 AM GMT+8 Last Updated 2 days ago',
        # 'JULY 09, 2022, 12:00 IST',
        # 'Jul 09, 2022 12:10 PM (IST)',
        # 'Jul 8, 2022,08:10am EDT',
        # "Maureen O'Hare, CNN • Published 9th July 2022",
        # "Jul 8, 2022 at 9:30 p.m.",
        # "13:38 (UTC+1) on Fri 8 Jul 2022",
        # "2022-09-08 13:38 UTC+8",
        # '1992/02/12 12:23:22+0900',
        # "Jul 08, 2022 7:09 PM PT",
        # "July 8, 2022 at 7:00 a.m. EDT",
        # "Fri, Jul 8 2022",
        # 'entries are due by Jan 4th, 2017 at 8:00pm',
        # 'July 17, 2022 5:25 PM ET',
        # 'yesterday is 2017/01/04',
        # 'I arrived in that city on January 4, 1937',
        # 'https://currentsapi.services/en/blog/2019/03/27/python-microframework-benchmark/.html',
        # 'Tue Jun 30 2015 12:00:00 GMT-0700 (PDT)',
        # 'Tue 2015 Dec 12 12:00:00 GMT-0700  PDT',
        # 'Tue Dec-11-1987T12:00:00 GMT-0700  PDT',
        # 'The time is 12/7/1958 20:50',
        # '1958.12.07T2:50 Pm+16:00',
        # '2021.04.01 13:51:39字数 282阅读 455',
        # '0.105-2021.04.01 13:51:39字数 282阅读 455',
        '2022-06-28 7-89',
        '2022 Jan 28 7-89',
        '28 Jan 2022 7-89',
        '你好 20220103 你',
        '0-100 2021-04-01 13:51:39字数 282阅读 455',
        '2022-06-28 7:30:00',
        'tEST ME 2022-06-28 09:30:00 on this',
        '2022/06/28 09:30:00',
        '2022 06 28 09:30:00',
        '2022.06.28 09:30:00',
        '1-30-2012 6:50',
        '2022年7月12日T20:50:00',
    ]

    for item in time_list:
        # t = get_datetime(item)
        t = mydatetime.directly_datetime(item)
        print(t)
        t2 = mydatetime.convert_timezone(t)
        print(t2)
        t3 = mydatetime.to_datetime_str(t2)
        print(t3)


    # for item in text_list:
    #     # t = get_datetime(item)
    #     # t = mydatetime.extract_date(item, date_only=False, day_first=True)
    #     t = mydatetime.extract_datetime(item, day_first=False)
    #     print(t)

