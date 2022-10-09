# -*- coding: utf-8 -*-
"""
Translator module that uses the Google Translate API.

Adapted from TextBlob
https://github.com/sloria/TextBlob/blob/dev/textblob/translate.py

Adapted from Terry Yin's google-translate-python.
Language detection added by Steven Loria.
"""
import codecs
import ctypes
import json
from urllib import request
from urllib.parse import quote as urlquote
from urllib.parse import urlencode


class TranslatorError(Exception):
    """Raised when an error occurs during language translation or detection."""
    pass


class NotTranslated(TranslatorError):
    """Raised when text is unchanged after translation. This may be due to the language
    being unsupported by the translator.
    """
    pass


_base_url = "http://translate.google.com/translate_a/t?client=webapp&dt=bd&dt=ex&dt=ld&dt=md&dt=qca&dt=rw&dt=rm&dt=ss&dt=t&dt=at&ie=UTF-8&oe=UTF-8&otf=2&ssel=0&tsel=0&kc=1"

headers = {
    'Accept': '*/*',
    'Connection': 'keep-alive',
    'User-Agent': (
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_6_8) '
        'AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.168 Safari/535.19')
}


def translate(source, from_lang='auto', to_lang='en', host=None, type_=None):
    data = {"q": source}
    url = u'{url}&sl={from_lang}&tl={to_lang}&hl={to_lang}&tk={tk}'.format(
        url=_base_url,
        from_lang=from_lang,
        to_lang=to_lang,
        tk=_calculate_tk(source),
    )
    response = _request(url, host=host, type_=type_, data=data)
    result = json.loads(response)
    
    # NOTE: this logic was changed to adapt to a new response format
    if isinstance(result, list):
        try:
            if isinstance(result[0], str):
                result = result[0]
            elif isinstance(result[0], list) and isinstance(result[0][0], str):
                result = result[0][0]  # ignore detected language
            else:
                raise TranslatorError('Unknown format of response data')
        except IndexError:
            pass
    _validate_translation(source, result)
    return result

def _validate_translation(source, result):
    """Validate API returned expected schema, and that the translated text
    is different than the original string.
    """
    if not result:
        raise NotTranslated('Translation API returned and empty response.')
    if result.strip() == source.strip():
        raise NotTranslated('Translation API returned the input string unchanged.')

def _request(url, host=None, type_=None, data=None):
    encoded_data = urlencode(data).encode('utf-8')
    req = request.Request(url=url, headers=headers, data=encoded_data)
    if host or type_:
        req.set_proxy(host=host, type=type_)
    resp = request.urlopen(req)
    content = resp.read()
    return content.decode('utf-8')


def _calculate_tk(source):
    """Reverse engineered cross-site request protection."""
    # Source: https://github.com/soimort/translate-shell/issues/94#issuecomment-165433715
    # Source: http://www.liuxiatool.com/t.php

    tkk = [406398, 561666268 + 1526272306]
    b = tkk[0]
    d = source.encode('utf-8')

    def RL(a, b):
        for c in range(0, len(b) - 2, 3):
            d = b[c + 2]
            d = ord(d) - 87 if d >= 'a' else int(d)
            xa = ctypes.c_uint32(a).value
            d = xa >> d if b[c + 1] == '+' else xa << d
            a = a + d & 4294967295 if b[c] == '+' else a ^ d
        return ctypes.c_int32(a).value

    a = b

    for di in d:
        a = RL(a + di, "+-a^+6")

    a = RL(a, "+-3^+b+-f")
    a ^= tkk[1]
    a = a if a >= 0 else ((a & 2147483647) + 2147483648)
    a %= pow(10, 6)

    tk = '{0:d}.{1:d}'.format(a, a ^ b)
    return tk
