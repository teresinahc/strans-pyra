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
Inthegra API Python wrapper.

This is a Python wrapper for the Inthegra API,
designed to provides some features not implemented
in the Inthegra API.

Accessing routes:

>>> import stranspyra as strans
>>> routes = strans.Route.all()
>>> routes[0]
<Route 0001 POTY VELHO B. ESPERANCA VIA ACARAPE>

Searching for a specific route:

>>> b401 = strans.Route.get_route(401)
>>> b401
<Route 0401 UNIVERSIDADE>

Getting the route's buses:

>>> buses = b401.get_buses()
>>> buses
[<Bus 02521 - 0401 UNIVERSIDADE>]

Accessing buses location:

>>> buses[0].lat, buses[0].long
(u'-5.04693500', u'-42.78294300')

Searching for routes:

>>> strans.Route.search('Universidade')
[<Route 0401 UNIVERSIDADE>, <Route 0365 UNIVERSIDADE CIRCULAR 2 VIA SHOPPING>,
 <Route 0563 UNIVERSIDADE CIRCULAR I VIA SHOPPING>,
 <Route 0626 HD-SACI-UFPI VIA SHOPPING>,
 <Route 0730 UNIVERSIDADE - CENTRO DUQUE DE CAXIAS>]

Retrieving stops:

>>> b401.get_stops()[:2]
[<Stop 2244 PC1 UFPI>, <Stop 875 RUA DIRCE DE OLIVEIRA 4 >]

Retrieving nearest stop:

>>> strans.Stop.nearest(-5.056221603326806,-42.79030821362158)
(<Stop 911 Campos Universitario - CCS>, Distance(0.0621590283922))

Retrieving nearest bus:

>>> bus = strans.Bus.nearest(-5.056221603326806,-42.79030821362158)
>>> bus
(<Bus 02764 - 0365 UNIVERSIDADE CIRCULAR 2 VIA SHOPPING>, Distance(0.72410974728))

"""

__version__ = '0.1.0'

from . import api
from .models import *

try:
    import settings
    api.auth()
except ImportError:
    pass
