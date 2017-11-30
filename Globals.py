'''
This module contains a bunch of data that needs to be globally accessible all
across AutoNifty.  That mostly means the config settings and stuff directly
related to or derived from them.
'''

import time
import datetime
import ConfigParser
import os

# These defaults largely come from AutoFox.  I wonder how many of them we need!
CONFIG_DEFAULTS = {
            'url':'about:blank',
            'basedir':'/home/change_this_setting_seriously',
            'updatetime':'0001',
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
today = None

def get_today():
    '''
    Returns the "today" tuple.  Will generate it if it hasn't been generated
    yet.
    '''
    global today

    if today is None:
        _generate_today()

    return today

def _generate_today():
    '''
    Generates a tuple describing what "today" is.  That is, what AutoNifty
    thinks the current day's comic should be, if said comic exists, after
    accounting for the local time zone, the exact time an update should occur,
    and other stuff like that.

    The tuple will be in filename order, which is to say (YYYY, MM, DD).  It
    can be retrieved with the get_today function.
    '''
    global config, today

    # First, get UTC time and apply the current time zone offset to get what
    # time it is "now".
    now = datetime.datetime.utcnow()
    tzoffset = config.getint('AutoNifty', 'tzoffset')
    hours = tzoffset / 100
    minutes = tzoffset % 100
    now += datetime.timedelta(hours=hours, minutes=minutes)

    # Now, determine what the update time is.  If "now" is before the update
    # time, rewind a day.
    updatetime = config.getint('AutoNifty', 'updatetime')
    updatehour = updatetime / 100
    updateminute = updatetime % 100

    if now.hour < updatehour or (now.hour == updatehour and now.minute < updateminute):
        now -= datetime.timedelta(days=1)

    # Now, spit that out as a tuple!
    today = (now.year, now.month, now.day)

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
        timezone = config.getint('AutoNifty', 'tzoffset')
    except ValueError:
        raise ValueError("The tzoffset config option MUST be something that resolves to an integer!")

    if timezone < -1200 or timezone > 1200 or abs(timezone) % 100 >= 60:
        raise ValueError("{} isn't a valid timezone offset!".format(timezone))

    # The update time has to be, y'know, a time.  However, we allow the user to
    # specify this time with a space in it, so just in case...
    updatetime = "".join(config.get('AutoNifty', 'updatetime').split())
    try:
        updatetime = int(updatetime)
    except ValueError:
        raise ValueError("The updatetime config option MUST be something that resolves to an integer!")

    if updatetime < 0 or updatetime > 2400 or updatetime % 100 >= 60:
        raise ValueError("{} isn't a valid update time!".format(updatetime))

    # If it's valid, stuff it back in, corrected.
    config.set('AutoNifty', 'updatetime', updatetime)

    # I guess we'll allow basedir to be relative if the user's really really
    # crazy, but we should still warn them.
    basedir = config.get('AutoNifty', 'basedir')
    workdir = config.get('AutoNifty', 'workdir')
    sitedir = config.get('AutoNifty', 'sitedir')
    if not basedir[0] == '/':
        print "WARNING: The basedir config option doesn't start with a slash, so we're assuming that's a relative path..."

    # However, it DOES have to END with a slash.  Let's clean that up now.
    if not basedir[-1] == '/':
        config.set('AutoNifty', 'basedir', basedir + '/')

    # Same with workdir and sitedir.
    if not workdir[-1] == '/':
        config.set('AutoNifty', 'workdir', workdir + '/')

    if not sitedir[-1] == '/':
        config.set('AutoNifty', 'sitedir', sitedir + '/')

    # If all goes well, mark the config as read!
    config_read = True

def get_directory_for(configthingy):
    '''
    Gets the full, effective path for a configuration directive.  That is, this
    will return the given config value with basedir prepended, as well as any
    other dependent directories (archivedir and comicsdir would have sitedir
    prepended, etc), unless the directory starts with a forward slash, in which
    case the path is assumed to be absolute regardless.
    '''
    global config, config_read
    if not config_read:
        raise RuntimeError("The config file hasn't been properly read yet!")

    # First off, basedir.  Everything comes from here (unless it's an absolute
    # path, but that won't happen often, hopefully).
    basedir = config.get('AutoNifty', 'basedir')

    # The second-level directories.
    sitedir = _attach_path(basedir, config.get('AutoNifty', 'sitedir'))
    workdir = _attach_path(basedir, config.get('AutoNifty', 'workdir'))

    # The first-or-second-level family!
    if configthingy == 'basedir':
        return basedir
    elif configthingy == 'sitedir':
        return sitedir
    elif configthingy == 'workdir':
        return workdir

    # The sitedir family!
    elif configthingy == 'comicsdir':
        return _attach_path(sitedir, config.get('AutoNifty', 'comicsdir'))
    elif configthingy == 'imagedir':
        return _attach_path(sitedir, config.get('AutoNifty', 'imagedir'))
    elif configthingy == 'archivedir':
        return _attach_path(sitedir, config.get('AutoNifty', 'archivedir'))

    # The workdir family!
    elif configthingy == 'parsedir':
        return _attach_path(workdir, config.get('AutoNifty', 'parsedir'))
    elif configthingy == 'datadir':
        return _attach_path(workdir, config.get('AutoNifty', 'datadir'))
    elif configthingy == 'uploaddir':
        return _attach_path(workdir, config.get('AutoNifty', 'uploaddir'))

    else:
        # Anything else is invalid.
        raise RuntimeError("{} isn't a valid directory-based config option!".format(configthingy))

def _attach_path(basepath, newpath):
    # If newpath starts with a forward slash, it's absolute, so just return
    # that.  Otherwise, attach basepath to the front of it.
    if newpath[0] == '/':
        return newpath
    else:
        return basepath + newpath
