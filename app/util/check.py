from datetime import datetime, time


def is_time_in_range(datetime_obj, start_time, end_time):
    return start_time <= datetime_obj.time() <= end_time


def is_check_time_in_range(datetime_obj):
    STANDARD_CHECK_TIME = 12 if datetime_obj.weekday() == 5 else 18
    start_time = datetime.combine(
        datetime_obj.date(), time(STANDARD_CHECK_TIME, 0)
    ).time()
    end_time = datetime.combine(datetime_obj.date(), time(23, 59, 59)).time()
    return is_time_in_range(datetime_obj, start_time, end_time)


# 기도회 기간 리스트
def prayer_check_dates():
    return [
        "2024-06-08",
        "2024-06-12",
        "2024-06-13",
        "2024-06-15",
        "2024-06-18",
        "2024-06-19",
        "2024-06-20",
        "2024-06-22",
        "2024-06-25",
        "2024-06-26",
        "2024-06-27",
        "2024-06-28",
        "2024-07-02",
        "2024-07-03",
        "2024-07-04",
        "2024-07-06",
        "2024-07-09",
        "2024-07-10",
        "2024-07-11",
        "2024-07-13",
    ]


def kor_week_day(datetime):
    """
    datetime을 넣으면 요일을 알려줍니다.
    """
    KOR_WEEK_DAY_LIST = ["월", "화", "수", "목", "금", "토", "일"]
    return KOR_WEEK_DAY_LIST[datetime.weekday()]
