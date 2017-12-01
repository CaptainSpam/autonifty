import Globals
import glob
import re
import datetime
import os

DATESTAMP_RE = re.compile("(?P<full>(?P<year>\\d{4})(?P<month>\\d{2})(?P<day>\\d{2}))")

class ComicBucket(object):
    '''
    The ComicBucket processes and contains all the comics in the system.  That
    is, it is what handles copying all "active" comics from the staging area
    into the real comics directory and sorting them into a big ol' list of
    active comic dates and their associated files (well, filenames).

    The basic storage here is a dictionary.  The keys are dates (as standard
    YYYYMMDD ints), the values are lists of strings representing that date's
    appropriate filenames.
    '''
    def __init__(self):
        self._active_comics = {}
        self._sorted_keys = []

    def __len__(self):
        '''
        The length of a ComicBucket is the number of ACTIVE comic dates.  This
        won't count the buffer.
        '''
        return len(self._active_comics)

    def keys(self):
        '''
        Gets all the keys in the bucket.  And by "keys", I mean "datestamps".
        These will come back sorted, because I can't imagine any reason why you
        WOULDN'T want a full list of comic dates sorted.
        '''
        return self._sorted_keys

    def get_comics_for(self, date):
        '''
        Gets the list of comics for the given datestamp.  This just pokes into
        the dictionary, so it'll raise a KeyError if the date doesn't exist.
        This is NOT a tuple, unlike the first/last/next/prev family, as you
        already have the date, in theory.
        '''
        return self._active_comics[date]

    def get_first(self):
        '''
        Gets the first date of comics.  This will be a tuple of the datestamp
        and the list of comics.
        '''
        key = self.keys()[0]
        comics = self.get_comics_for(key)
        return (key, comics)

    def get_last(self):
        '''
        Gets the most recent date of comics.  This will be a tuple of the
        datestamp and the list of comics.
        '''
        key = self.keys()[-1]
        comics = self.get_comics_for(key)
        return (key, comics)

    def get_next(self, datestamp):
        '''
        Gets the next comic date in sequence from the given one.  This will be a
        tuple of the datestamp and the list of comics, unless it's the last date
        available, in which case, it will be None.  ValueError will be raised if
        the given date doesn't exist.

        Really, if you're iterating, you might just want to use keys() and work
        with that.
        '''
        index = self.keys().index(datestamp)
        if index == len(self.keys()) - 1:
            return None
        key = self.keys()[index + 1]
        comics = self.get_comics_for(key)
        return (key, comics)

    def get_prev(self, datestamp):
        '''
        Gets the previous comic date in sequence from the given one.  This will
        be a tuple of the datestamp and the list of comics, unless it's the
        first date available, in which case, it will be None.  ValueError will
        be raised if the given date doesn't exist.

        Seriously, this and get_next() are just-in-case, at least for now.  You
        probably want to just iterate from keys().
        '''
        index = self.keys().index(datestamp)
        if index == 0:
            return None
        key = self.keys()[index - 1]
        comics = self.get_comics_for(key)
        return (key, comics)

    def filter_bucket(self):
        '''
        This moves any comic files that should now be considered live from the
        uploaddir into the comicsdir so they may later be indexed by
        read_bucket().  As such, this makes no changes to the internal state of
        ComicBucket.

        It does, however, return the number of comic files moved.  This is in no
        way guaranteed to have any relation to the number of new dates with
        comic updates.
        '''
        uploaddir = Globals.get_directory_for('uploaddir')
        comicsdir = Globals.get_directory_for('comicsdir')
        today = Globals.get_today()

        # All files report in!
        filelist = glob.glob(uploaddir + '*')
        filesmoved = 0

        # And just what ARE those files?  Funny you should ask...
        for f in filelist:
            if not os.path.isfile(f):
                continue

            # Strip it down to just the name, but keep the full path.  We may
            # need it in a sec.
            fname = f[len(uploaddir):]

            match = re.search(DATESTAMP_RE, fname)
            if match is None:
                # Bad file name?  No datestamp?
                print "filter_bucket: Comic file {} has no datestamp in its name, ignoring...".format(fname)
                continue
            else:
                # Bad date?
                year = int(match.group('year'))
                month = int(match.group('month'))
                day = int(match.group('day'))

                try:
                    datetime.datetime(year=year, month=month, day=day)
                except ValueError:
                    print "filter_bucket: Comic file {} contains an invalid date, ignoring...".format(fname)
                    continue

                # So it's a valid filename.  Is it, however, TODAY (or earlier)???
                if year < today[0] or (year == today[0] and month < today[1]) or (year == today[0] and month == today[1] and day <= today[2]):
                    # It's today!  It's today!  Hooray!  Hooray!  Move the file!
                    os.rename(f, comicsdir + fname)
                    filesmoved += 1

        # Done!  Return how many we got.  I don't know why, maybe we want to
        # report that later.
        return filesmoved

    def read_bucket(self):
        '''
        This reads in the bucket as it exists on the filesystem right now.
        Call filter_bucket() first to put the active comics into the correct
        directory.
        '''
        comicsdir = Globals.get_directory_for('comicsdir')

        # CLEAR!
        self._active_comics = {}

        # Pop open the file list.  All of them.
        filelist = glob.glob(comicsdir + '*')

        # Now, we don't have any clue what order these are in, so we have to
        # build up the entire dictionary on the fly.  Fortunately, we also
        # don't have any clue what order the dictionary is in once we've stored
        # it, so it fits in.
        for f in filelist:
            # Ignore directories.  Just plain files.
            if not os.path.isfile(f):
                # No warning, though.  This is okay.
                continue

            f = f[len(comicsdir):]

            # Does the filename contain a datestamp?  That's eight digits.
            match = re.search(DATESTAMP_RE, f)

            if match is None:
                print "read_bucket: Comic file {} has no datestamp in its name, ignoring...".format(f)
                continue
            else:
                # Okay, we've got a date.  Is it legal?
                try:
                    datetime.datetime(year=int(match.group('year')), month=int(match.group('month')), day=int(match.group('day')))
                except ValueError:
                    # Whoops.  That's not valid at all.
                    print "read_bucket: Comic file {} contains an invalid date, ignoring...".format(f)
                    continue

                # It's valid!  Add the date and the file in!  First, initialize
                # a list if we don't have that date yet.
                full = match.group('full')
                if full not in self._active_comics:
                    self._active_comics[full] = []

                self._active_comics[full].append(f)

        # Now, though we don't know what order we get the files in, we DO need
        # to make sure each individual date's list is in alphabetical order, as
        # that's the order in which the files will appear on the site.
        for l in self._active_comics:
            self._active_comics[l].sort()

        # Pre-sort the keys, too, so we're not just doing that literally every
        # time we need a comic.
        self._sorted_keys = sorted(self._active_comics.keys())

