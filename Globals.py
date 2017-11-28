'''
This module contains a bunch of data that needs to be globally accessible all
across AutoNifty.  That mostly means the config settings and stuff directly
related to or derived from them.
'''

import time
import ConfigParser
import os

# These defaults largely come from AutoFox.  I wonder how many of them we need!
CONFIG_DEFAULTS = {
            'url':'about:blank',
            'basedir':'/home/change_this_setting_seriously',
            'updatetime':'2300',
            'updateday':'same',
            'tzoffset':str(int(float(-time.timezone) / 36)),
            'captionsfile':'captions.txt',
            'comicsdir':'comics/',
            'imagedir':'images/',
            'dailydir':'d/',
            'uploaddir':'comics/',
            'sitedir':'public_html/',
            'workdir':'workspace/',
            'parsedir':'pages/',
            'datadir':'data/',
            'storyfile':'storyline.txt',
            'logfile':'autonifty.log',
            'indexfile':'index.html',
            'storylinebanners':'storylinebanners.txt',
            'dailyext':'.html',
            'usecssnavbuttons':'0',
            'lastday':'',
            'firstday':'',
            'previousday':'',
            'nextday':'',
            'lastdayghosted':'',
            'firstdayghosted':'',
            'previousdayghosted':'',
            'nextdayghosted':'',
            'storystart':'storystart.gif',
            'dailytemplate':'dailytemplate.html',
            'jsprefix':'af_',
            'storylineusedate':'0',
            'storylineusejavascript':'1',
            'storylineuseplain':'1',
            'bigcalwidth':'3',
            'calbacka':'#d0d0d0',
            'calbackb':'#b0b0b0',
            'calhighlight':'#ffffff',
            'calnolink':'#000000',
            'rssfullgenerate':'0',
            'rssfullfilename':'comicfeed.rdf',
            'rsslitegenerate':'0',
            'rsslitefilename':'comicfeedlite.rdf',
            'rsslimit':'10',
            'rsstitle':'DEFAULT TITLE',
            'rsslink':'http://localhost',
            'rssdescription':'Edit this in the config file!',
            'rsscopyright':'Something something copyright'
        }

config = ConfigParser.RawConfigParser(defaults=CONFIG_DEFAULTS, allow_no_value=True)
config_read = False

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

def read_config(filename):
    '''
    Reads a config file into the config parser, checking to make sure everything
    is sane (i.e. all booleans are booleans, all int values are ints).  This
    will raise exceptions if anything goes wrong.  If an exception HAS been
    raised, assume the config object is no longer in a valid state and deal
    with the problem.
    '''
    global CONFIG_DEFAULTS, config_read, config

    if config_read:
        # We already did this!
        raise Exception("The config file's already been parsed!  Ignoring...")

    # Pop open the file.  Things might be raised left and right at this point.
    config.readfp(open(filename))

    # Presumably, open would've raised if the file can't be opened.  So we
    # should have a proper config now.  Let's go through the sanity checks!

    # Everything needs to be in the "AutoNifty" section.
    if not config.has_section('AutoNifty'):
        raise NoSectionError('AutoNifty')

    # Each of these must be boolean-like.
    checking = 'usecssnavbuttons'
    try:
        config.getboolean('AutoNifty', checking)
        checking = 'storylineusedate'
        config.getboolean('AutoNifty', checking)
        checking = 'storylineusejavascript'
        config.getboolean('AutoNifty', checking)
        checking = 'storylineuseplain'
        config.getboolean('AutoNifty', checking)
        checking = 'rssfullgenerate'
        config.getboolean('AutoNifty', checking)
        checking = 'rsslitegenerate'
        config.getboolean('AutoNifty', checking)
    except ValueError:
        raise ValueError("The {} config option MUST be something that resolves to True or False!".format(checking))

    # The time zone offset has to be an integer between -1200 and 1200.
    timezone = 0
    try:
        timezone = int(config.getint('AutoNifty', 'tzoffset'))
    except ValueError:
        raise ValueError("The tzoffset config option MUST be something that resolves to an integer!")

    if timezone < -1200 or timezone > 1200 or abs(timezone) % 100 >= 60:
        raise ValueError("{} isn't a valid timezone offset!".format(timezone))

    # updateday must be "same" or "previous".
    if config.get('AutoNifty', 'updateday') not in ['same', 'previous']:
        raise ValueError("{} isn't a valid updateday setting! (it has to be either 'same' or 'previous')".format(config.get('AutoNifty', 'updateday')))

    # If all goes well, mark the config as read!
    config_read = True
