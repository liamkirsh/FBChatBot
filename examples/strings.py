import requests
import sys
from collections import OrderedDict

MEME_HELP = """Syntax: meme keyword top text (optional: / bottom text). Supported keywords:\n\t{}"""

def get_meme_templates():
    try:
        r = requests.get("https://memegen.link/api/templates/", timeout=10)
    except requests.exceptions.RequestException as e:
        sys.stderr.write("Error reading meme templates: {}".format(e))
        return

    j = r.json(object_pairs_hook=OrderedDict)
    memes = ('{}: "{}"'.format(name, kword.rsplit('/', 1)[-1])
             for name, kword in j.iteritems())
    return MEME_HELP.format('\n\t'.join(memes))
