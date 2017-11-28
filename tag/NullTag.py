from Tag import Tag

class NullTag(Tag):
    '''
    A NullTag acts as if this weren't a tag, inserting the literal tag back into
    the HTML.  This is an alternative to InvalidTag, which presents an error
    back to the user.
    '''
    def __init__(self):
        super(NullTag, self).__init__()
        self._tagname = "NullTag"

    def do_tag(self, match, parser):
        if(not match or not match.group(1)):
            return "UNMATCHED NULLTAG!"

        toreturn = match.group(1)

        if(match.group(2)):
            toreturn += " " + format(match.group(2))

        return toreturn
