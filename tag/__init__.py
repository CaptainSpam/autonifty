import glob
import importlib

TAGS = {}

# Open up all the tag files in this directory and attempt to import them as
# Python modules.  Each one will then get exactly one instance which will be
# called from TagFactory to do parsing (this means we won't have to keep
# creating new objects over and over and over again).
filelist = glob.glob('tag/*Tag.py')

for f in filelist:
    f = f[len("tag/"):-len(".py")]

    try:
        module = importlib.import_module("tag.{}".format(f))
        classFromModule = getattr(module, f)
        TAGS[f] = classFromModule()
    except:
        print "Couldn't import tag named {}, skipping...".format(f)

def reset_tags_for_day():
    for t in TAGS:
        TAGS[t].reset_for_day()

def reset_tags_for_page():
    for t in TAGS:
        TAGS[t].reset_for_page()
