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
        pass
