class Tag(object):
    '''
    A Tag is a single set of instructions to replace a given unparsed tag.
    This can be as simple as inserting the current date or the comic's name to
    more complex nonsense like parsing a new page (include), determining which
    comic to put on a certain request, or crazy regex substitution.
    '''
    def __init__(self):
        self._tagname = "Tag"

    def do_tag(self, match, parser):
        '''
        Does tag stuff.  This gets the required match data and returns whatever
        should go in this tag's place.  The Parser will know what to do with it.
        '''
        pass

    def reset_for_day(self):
        '''
        Tags are instanced once per parsing session in the current
        implementation.  This method resets anything a tag needs reset when
        starting on a new comic day.  Just in case.
        '''
        pass

    def reset_for_page(self):
        '''
        Tags are instanced once per parsing session in the current
        implementation.  This method resets anything a tag needs reset when
        starting on a new page that isn't a new comic day.
        '''
        pass
