# Utility functions
import re

def unescape(s):
    s = s.replace("&lt;", "<")
    s = s.replace("&gt;", ">")
    s = s.replace("&quot;",'"')
    s = s.replace("&apos;", "'")
    s = s.replace("&#39;", "'")


    # this has to be last:
    s = s.replace("&amp;", "&")
    return s

def uppercasewords(display):
    words = display.split(" ")
    return uppercasewordlist(words)

def uppercasewordlist(words):

    new_words = []
    for a in words:
        # camel case them
        if (a <> ""):
            if a == 'GB':
                pass    # dont bother adding GB
            else:
                uword = a[0:1].upper()
                uword += a[1:].lower()
                new_words.append( uword )

    return " ".join( new_words )


def pretty_display(display):
      raw_words = display.split(" ")

      pat = re.compile("[0-9]{4}")
      words = []
      extra_words = []

      # remove load sof numerics
      if len(raw_words) > 2:
        words = raw_words[0:2]
        for a in raw_words[2:]:
          if pat.search(a) == None:
            words.append(a)
          else:
            extra_words.append(a)
      else:
        words = raw_words[:]

      return uppercasewordlist(words), uppercasewordlist(extra_words)
      #return " ".join(words), " ".join(extra_words)