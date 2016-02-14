import datetime
import data


def create_log(message, level):
    logm = data.make_log(datetime.datetime.now(), message, level)
