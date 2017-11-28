import importlib
import string
from InvalidTag import InvalidTag
from NullTag import NullTag
from tag import TAGS

class TagFactory(object):
    def __init__(self, parser):
        self._parser = parser

    def execute_tag(self, match):
        '''
        Executes a Tag from a given MatchObject.  That is, this should come in
        straight from the Parser's regex matcher.  As such, the first group of
        the match should be the tag name with underscores, and the second group
        should be the param list, if one exists.  Tag name conversion is simple:
        Each underscore in a tag separates a word, and each word is capitalized,
        with "Tag" added to the end.  Meaning, ***tag_name_thing*** should be
        passed in as "tag_name_thing" and will result in trying to execute
        do_tag on a tag called "TagNameThingTag".  Don't add a "_tag" suffix.

        The params should be passed in exactly as they appear on the unparsed
        tag.
        '''
       
        if(not match or not match.group(1)):
            # This really shouldn't happen, but if there's no tagname, just
            # return the matching text as a NullTag.
            return TAGS["NullTag"].do_tag(match, self._parser)

        # Sure, capwords will cap the words nicely, but then it puts the
        # underscores right back in...
        tagname = "".join(string.capwords(match.group(1).lower(), "_").split("_")).append("Tag")

        if(not tagname in TAGS):
            tagname = "NullTag"
        
        return TAGS[tagname].do_tag(match, self._parser)

