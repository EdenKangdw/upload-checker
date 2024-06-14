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
