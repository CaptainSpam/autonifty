from Tag import Tag

class InvalidTag(Tag):
    '''
    InvalidTag is more of a placeholder in the event that a real tag can't be
    imported for whatever reason (usually that the tag doesn't exist).
    '''
    def __init__(self):
        super(InvalidTag, self).__init__()
        self._tagname = "InvalidTag"
        self._response = "ERROR: Invalid tag!"

    def set_response(self, response):
        self._response = response

    def do_tag(self, match, parser):
        return self._response
