import re
from tag.TagFactory import TagFactory
import Globals

# This oughta match anything tag-like.  Group 1 is the tag name, group 2 is any
# amount of params it might have (can be None).
TAG_RE = re.compile("\*\*\*\s*(\S+?)(?:\s+(.+?))?\s*\*\*\*")

class Parser(object):
    '''
    The Parser is what gets looped through to parse files.  Ultimately, this is
    a giant regex thingamajig.  You give it a file (or text), it returns back a
    block of text parsed to perfection.

    This also stores a bunch of state data about the current parse operation.
    This can be useful for some tags.
    '''
    def __init__(self):
        # TODO: Needs some way to get global data!  Comic lists, the storyline,
        # etc, etc...
        self._seen_files = {}
        self._tag_factory = TagFactory(self)
        self._today = Globals.get_today()
        self._requested_date = self._today

    def parse_file_by_name(self, filename):
        '''
        Parses a file, given its name.  It'll open up the file or bail out if it
        can't read it (it WILL return text in that case!).  Then it shoves the
        whole thing line-by-line to _parse_line and returns the result.

        This returns False if the file's already been seen in this include
        chain, though.  Check for that.
        '''
        ###
        # TODO: Normalize the filenames and paths.  We need to know what the
        # root of the webpage path is, stop any file read that tries to go
        # outside of that root, and translate any absolute paths into something
        # rooted at the webpage root instead of the filesystem root.  Safety
        # first, children!
        ###
        if(not isinstance(filename, str)):
            return "ERROR: Something that wasn't a string was passed to parse_filename!"

        # First, check _seen_files.
        if(self._mark_file_seen(filename) == False):
            return "ERROR: This is an include loop!  You already included {}!".to_parse

        # Open 'er up and read it in!
        try:
            fileobj = open(filename)

            toreturn = ""

            for line in fileobj:
                toreturn += self._parse_line(line)

            # Make sure we declare we're done with it, too.
            self._done_with_file(filename)
            return toreturn
            
        except IOError as ioe:
            return "ERROR: Something went wrong reading file {}!".format(filename)

    def parse_text(self, to_parse):
        '''
        Parses a big ol' chunk of text.  It'll do this line-by-line.  All
        newlines will be preserved.
        '''
        lines = to_parse.splitlines(True)
        toreturn = ""
        for line in lines:
            toreturn += self._parse_line(line)

        return toreturn

    def _parse_line(self, line):
        '''
        Parses things one line at a time.  This'll return a fully parsed line.
        '''
        return re.sub(TAG_RE, self._tag_factory.execute_tag, line)

    def _mark_file_seen(self, filename):
        '''
        This adds a file to the list of files we've already seen in this parse.
        That is, this is called during an IncludeTag operation.  If it's already
        there, this simply returns False.

        Note that this won't get called during a parse_text call, as there's no
        filename there.
        '''
        if(filename in self._seen_files):
            return False
        else:
            self._seen_files[filename] = 1
            return True

    def _done_with_file(self, filename):
        '''
        Marks a previously-seen file as done, removing it from the list of seen
        files.  This will return True if the file was in there, False if it
        wasn't.
        '''
        if(filename in self._seen_files):
            del self._seen_files[filename]
            return True
        else:
            return False

    def get_today(self):
        '''
        Gets "today", as was calculated when this Parser was made.  This is for
        Tags that need to know what day it should think it is.
        '''
        return self._today

    def set_requested_date(self, date_tuple):
        '''
        Sets the requested comic.  Note that at this point, it's assumed the
        comic exists; stop and do something else beforehand if it doesn't.

        This is a tuple in filename order (YYYY, MM, DD).
        '''
        self._requested_date = date_tuple

    def get_requested_date(self):
        '''
        Regardless of "today", this gets the requested comic date.  This is
        only valid when perusing the archives.  If nothing else calls
        set_requested_date, this will match "today".
        '''
        return self._requested_date
