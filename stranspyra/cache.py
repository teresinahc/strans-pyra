# Copyright (c) 2016 Renato Alencar <renatoalencar.73@gmail.com>
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify,
# merge, publish, distribute, sublicense, and/or sell copies of
# the Software, and to permit persons to whom the Software is furnished
# to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

"""
Implements object caching using decorators.
"""

import time
import threading

try:
    import settings
    USE_CACHE = settings.USE_CACHE
except ImportError:
    USE_CACHE = False

__memcache__ = dict()
__lock__ = threading.RLock()
__timestamps__ = dict()


def cached(method):
    """
    Static memory cache system decorator.
    """

    if not USE_CACHE:
        return method

    def _cache_wrapper(self, *args, **kwargs):
        global __memcache__, __lock__

        if method.__name__ in __memcache__.get(self.code, {}):
            return __memcache__[self.code][method.__name__]

        with __lock__:
            ret = method(self, *args, **kwargs)
            if self.code not in __memcache__:
                __memcache__[self.code] = dict()
            __memcache__[self.code][method.__name__] = ret
            return ret
    return _cache_wrapper


def timestampcache(expires):
    """
    Timestamp based memory cache system decorator.

    @param expires: expiration time in seconds.
    """

    def _decorator_wrapper(method):
        if not USE_CACHE:
            return method

        def _cache_wrapper(self, *args, **kwargs):
            global __memcache__, __timestamps__, __lock__

            now = time.time()
            last_update = __timestamps__.get(
                self.code, {}
            ).get(
                method.__name__, now
            )

            if last_update > now:
                return __memcache__[self.code][method.__name__]

            with __lock__:
                ret = method(self, *args, **kwargs)
                if self.code not in __memcache__:
                    __memcache__[self.code] = dict()
                    __timestamps__[self.code] = dict()
                __memcache__[self.code][method.__name__] = ret
                __timestamps__[self.code][method.__name__] = now + expires
                return ret
        return _cache_wrapper
    return _decorator_wrapper
