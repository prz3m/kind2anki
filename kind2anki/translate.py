#!/usr/bin/env python
# ----------------------------------------------------------------------------
# "THE BEER-WARE LICENSE" (Revision 42):
# <terry.yinzhe@gmail.com> wrote this file. As long as you retain this notice you
# can do whatever you want with this stuff. If we meet some day, and you think
# this stuff is worth it, you can buy me a beer in return to Terry Yin.
#
# Now google has stop providing free translation API. So I have to switch to
# http://mymemory.translated.net/, which has a limit for 1000 words/day free
# usage.
#
# The original idea of this is borrowed from <mort.yao@gmail.com>'s brilliant work
#    https://github.com/soimort/google-translate-cli
# ----------------------------------------------------------------------------
'''
This is a simple, yet powerful command line translator with google translate
behind it. You can also use it as a Python module in your code.
'''
import json
from textwrap import wrap
try:
    import urllib2 as request
    from urllib import quote
except:
    from urllib import request
    from urllib.parse import quote

class Translator:
    def __init__(self, to_lang, from_lang='en'):
        self.from_lang = from_lang
        self.to_lang = to_lang

    def translate(self, source):
        if self.from_lang == self.to_lang:
            return source
        self.source_list = wrap(source, 1000, replace_whitespace=False)
        return ' '.join(self._get_translation_from_google(s) for s in self.source_list)

    def _get_translation_from_google(self, source):
        json5 = self._get_json5_from_google(source)
        data = json.loads(json5)
        translation = data['responseData']['translatedText']
        if not isinstance(translation, bool):
            return translation
        else:
            matches = data['matches']
            for match in matches:
                if not isinstance(match['translation'], bool):
                    next_best_match = match['translation']
                    break
            return next_best_match

    def _get_json5_from_google(self, source):
        escaped_source = quote(source, '')
        headers = {'User-Agent':
                   'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_6_8) AppleWebKit/535.19\
                   (KHTML, like Gecko) Chrome/18.0.1025.168 Safari/535.19'}
        api_url = "http://mymemory.translated.net/api/get?q=%s&langpair=%s|%s"
        req = request.Request(url=api_url % (escaped_source, self.from_lang, self.to_lang),
                              headers=headers)

        # url="http://translate.google.com/translate_a/t?clien#t=p&ie=UTF-8&oe=UTF-8"
        # +"&sl=%s&tl=%s&text=%s" % (self.from_lang, self.to_lang, escaped_source)
        # , headers = headers)
        r = request.urlopen(req)
        return r.read().decode('utf-8')