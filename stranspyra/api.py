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

import requests
import time

import settings
from .exceptions import APIServerError

token = ''

def date():
    """
    Returns the current time formated with HTTP format.

    @return: `str`
    """
    return time.strftime('%a, %d %b %Y %H:%M:%S GMT')

def auth():
    """
    Authenticates the user using the url, application key,
    email and the password.

    @return: a `dict` object with the keys `token` and `minutos`,
        from json returned from the API.
    """

    global token
    endpoint = '/signin'

    url = settings.URL
    key = settings.API_KEY

    res = requests.post(
        url + endpoint,
        headers = {
            'date': date(),
            'x-api-key': key,
        },
        json = {
            'email': settings.EMAIL,
            'password': settings.PASSWORD
        },
        **settings.REQUEST_OPTIONS
    )

    try:
        res = res.json()
        token = res['token']
    except Exception:
        pass

    return res

def get(endpoint, **kwargs):
    """
    Makes a GET request to the API, sending the `token` without
    need to send it all the times.

    @param endpoint: the endpoint URL (e.g.: '/linhas').

    keyword args passed as URL params.

    `settings.REQUEST_OPTIONS` are passed as kwargs to
        `requests.get`.

    @return: a json decoded object.

    Raises `APIServerError` if it returns message with
        'api.error'.
    """

    global token

    url = settings.URL
    key = settings.API_KEY

    res = requests.get(
        url + endpoint,
        headers = {
            'date': date(),
            'x-api-key': key,
            'x-auth-token': token,
        },
        params = kwargs,
        **settings.REQUEST_OPTIONS
    )

    jres = res.json()
    if isinstance(jres, dict) and jres.get('message', '').startswith('api.error'):
        if jres['message'] == 'api.error.token.expired' and token is not None:
            auth()
            return get(endpoint, **kwargs)

        raise APIServerError(jres['message'])

    return jres
