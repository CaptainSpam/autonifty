import time

def get_today():
    '''
    Returns a tuple describing what "today" is.  That is, what AutoNifty thinks
    the current day's comic should be, if said comic exists, after accounting
    for the local time zone, the exact time an update should occur, and other
    stuff like that.

    The tuple will be in filename order, which is to say (YYYY, MM, DD).
    '''
    ###
    # TODO: Need to get a configuration file to adjust the update time, time
    # zone, etc!
    ###
    now = time.localtime()

    return (now.tm_year, now.tm_mon, now.tm_mday)
