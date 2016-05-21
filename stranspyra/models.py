# -*- coding: utf8 -*-
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
Strans endpoints mapped models.

Provides access to each endpoint of the Inthegra API.
And adds extra features like search for the nearest bus
or stop.

Besides that, the models provides links betweens the
endpoints that the API itself does not provide.

eg.:

>>> Route.search(401)
[<Route 0401 UNIVERSIDADE>, <Route T0401 BOA VISTA/AV.3/CENTRO/PQ ALVORADA/MUTIRAO - EXT 01>]

"""

from geopy.distance import distance
import itertools

import settings
from . import api
from .exceptions import *
from .cache import cached, timestampcache

class Model(object):
    """
    The model base.

    The `Model` class is the base for all other models. You must specify
    the `endpoint` of the model and the mapper. The `mapper` is a dictionary
    where the keys are the API keys of the object and the values are its
    respective attribute name on model.

    This mapping is made in order to escape the anti-pattern objects keys
    of the Inthegra API. The keys are all in portuguese and CamelCase style.
    """

    endpoint = None
    mapper = {}

    def __init__(self, obj=None):
        """
        @constructor

        @param obj: The object returned by the Inthegra API, as described
            in the mapper object.
        """

        self.obj = obj
        if self.obj:
            self.to_python()

    def to_python(self):
        """
        Maps the Inthegra's endpoint object to Python attributes
        of the `mapper`.

        Note: It does not make casting yet.
        """

        for key, attr in self.mapper.items():
            setattr(self, attr, self.obj[key])

    @classmethod
    def all(cls):
        """
        All the endpoints of the API returns all of its elements if
        called without params. This method returns all elements of
        a endpoint as objects.

        @return: A list of instances of the model.
        """

        info = api.get(cls.endpoint)

        return map(cls, info)

    def __eq__(self, other):
        """
        All objects of the API have the `code` attribute. The mappers
        creates it from something like `Codigo...`. This method allows
        compare two objects of the API, even they are not the same
        object in the memory.

        @param other: A instance of the same type of `self`.

        @return: Boolean, if this is equal to `other`.
        """
        return self.code == other.code

    def update(self):
        """
        Retrieves all the elements of the endpoint, search
        for the current one and updates.
        """

        objs = self.__class__.all()
        this = filter(lambda x: x == self, objs)
        self.obj = this[0].obj
        self.to_python()

    @classmethod
    def search(cls, pattern):
        """
        This method is a wrapper to the `busca` param of
        some endpoints of the API.

        @param pattern: Something serializable by `requests` lib.
            You can use the code of some object or something
            like a neighborhood for `Route`.

        @return: A list of instances of `cls`.
        """
        info = api.get(cls.endpoint, busca=pattern)

        return map(cls, info)

    @classmethod
    def filter(cls, func):
        """
        Applies a filter through `filter` Python function,
        using `func` and all the objects of the endpoint.

        @param func: A callable what returns boolean coercible value,
            receiving a `cls` instance.

        @return: A list of `cls` instances.
        """
        return filter(func, cls.all())

class Route(Model):
    """
    Provides a model to access the endpoint `linhas`.

    @attribute code: A unique `str` that identifies the route (e.g.: '0401').
    @attribute description: A `str` route description (e.g.: 'UNIVERSIDADE').
    @attribute source: A `str` that identifies the route's start point.
    @attribute dest: A `str` that identifies the route's end point.
    @attribute circular: A boolean, if the route returns to the source.
    """

    endpoint = '/linhas'
    mapper = {
        'CodigoLinha': 'code',
        'Denomicao': 'description',
        'Origem': 'source',
        'Retorno': 'dest',
        'Circular': 'circular'
    }

    @classmethod
    def traceroute(self, source, dest):
        """
        Trace a route between `source` and `dest`.

        First, find the nearest stop to `source` and the nearest to `dest`
        and try to find a common route to both. Otherwise, fallbacks searching
        for all routes of the `source` stop and `dest` stop, choosing the one
        what is nearest to the `source` or `dest`.

        @param source: a pair latitude and longitude
        @param dest: a pair latitude and longitude

        @return: a tuple like ((<source stop>, <distance to the nearest stop>),
            (<dest stop>, <distance to the nearest stop>), <route>)
        """

        sourcestop, dsrc = Stop.nearest(source[0], source[1])
        deststop, ddst = Stop.nearest(dest[0], dest[1])
        sourceroutes = sourcestop.get_routes()
        destroutes = deststop.get_routes()

        for i,j in itertools.product(sourceroutes, destroutes):
            if i == j:
                return (sourcestop, dsrc), (deststop, ddst), i

        dist, stop, route = min(
            min(Stop.nearest(source[0], source[1], route=route)[::-1] + (route,) for route in destroutes),
            min(Stop.nearest(dest[0], dest[1], route=route)[::-1] + (route,) for route in sourceroutes)
        )

        sourcestop = Stop.nearest(source[0], source[1], route=route)
        deststop = Stop.nearest(dest[0], dest[1], route=route)

        return sourcestop, deststop, route

    @cached
    def get_stops(self):
        """
        Return all the stops of a route, using `paradasLinha` endpoint.

        This method is permanently cached when this is called for a
        object, and it's cached for that object.

        @return: A list of `Stop` instances.
        """

        info = api.get('/paradasLinha', busca=self.code)

        # Handling a unknown erro on Inthegra API
        # Bad bad documented?
        if info.get('code', 0) == 130:
            return []

        return map(Stop, info['Paradas'])

    @timestampcache(30)
    def get_buses(self):
        """
        Return all the buses of a route, using `veiculosLinha` endpoint.

        This method is cached for 30 seconds, for the object from it was
        called.

        @return: A list of `Bus` instances.
        """

        info = api.get('/veiculosLinha', busca=self.code)

        if info.get('code', 0) == 130:
            return []

        buses = []
        for i in info['Linha']['Veiculos']:
            bus = Bus(i)
            # It's saves the real route at `__route__`, cause
            # get_route is a cached-lazy method.
            bus.__route__ = self
            buses.append(bus)

        return buses

    @classmethod
    def get_route(cls, route):
        """
        Return the first route that `code` matches exactly with `route`.

        You can use a int with `route` too:

        >>> Route.get_route(401)
        <Route 0401 UNIVERSIDADE>

        @param route: A int or a str coercible value.

        @return: A `Route` isinstance.

        Raises `RouteNotFoundError` if no route was found.
        """

        lines = cls.search(route)
        for i in lines:
            code = i.code
            if isinstance(route, int):
                try:
                    if int(i.code) == route:
                        return i
                except ValueError:
                    if i.code == str(route).zfill(4):
                        return i
            else:
                if route == i.code:
                    return i

        raise RouteNotFoundError('Linha {0} não encontrada.'.format(line))

    def __repr__(self):
        return u'<Route {0} {1}>'.format(self.code, self.description)

class Stop(Model):
    """
    Model for `paradas` endpoint.

    @attribute code: A unique `int` that identifies the stop.
    @attribute description: A `str` description.
    @attribute address: A `str`, the stop's address location.
    @attribute lat: A `float` coercible `str`.
    @attribute long: A `float` coercible `str`.
    """

    endpoint = '/paradas'
    mapper = {
        'CodigoParada': 'code',
        'Denomicao': 'description',
        'Endereco': 'address',
        'Lat': 'lat',
        'Long': 'long'
    }

    def __repr__(self):
        return u'<Stop {0} {1}>'.format(self.code, self.description)

    @cached
    def get_routes(self):
        """
        Returns all the routes that have this stop.

        Warning: Don't use that if it's not required.
            This method is too slow and several requests.
            However, it's useful to find what bus should
            be got.

        @return: A list of `Route` instances.
        """
        ## FIXME: **too slow**

        lines = Route.all()
        r = []
        for line in lines:
            if filter(lambda x: x == self, line.get_stops()):
                r.append(line)

        return r

    @classmethod
    def nearest(cls, lat, long, **kwargs):
        """
        Search for the nearest stop from `lat` and `long`
        params.

        You should specify the stops to search, default is
        `Stop.all()`.

        @param lat: A float coercible value of latitude (eg.: -5.065533).
        @param long: A float coercible value of longitude (eg.: -42.065533).

        keywords params:
            stops:
                A list of `Stop` instance.
            route:
                A `Route` instance.

        @return: A tuple with a `Stop` object and a `Distance`
            object (see geopy.distance).
        """

        if kwargs.get('stops', False):
            stops = kwargs['stops']
        elif kwargs.get('route', False):
            stops = kwargs['route'].get_stops()
        else:
            stops = cls.all()

        dists = map(lambda stop: distance(
                (stop.lat, stop.long),
                (lat, long)
            ), stops)

        return min(zip(dists, stops))[::-1]

class Bus(Model):
    """
    Model for `veiculos` endpoint.

    @attribute code: a `int` unique identify.
    @attribute lat: a `float` coercible `str` for latitude.
    @attribute long: a `float` coercible `str` for longitude.
    @attribue hour: the last location update of the bus.
    """
    endpoint = '/veiculos'
    mapper = {
        'CodigoVeiculo': 'code',
        'Lat': '__lat__',
        'Long': '__long__',
        'Hora': 'hour'
    }
    __route_code__ = None
    __route__ = None

    @property
    def route(self):
        """
        Returns the bus' route.

        @return: A `Route` instance.
        """

        if self.__route__ is not None:
            return self.__route__
        if self.__route_code__ is not None:
            self.__route__ = Route.get_route(self.__route_code__)
            return self.__route__

    @classmethod
    def all(cls):
        """
        Retrieves all buses from the API.

        This endpoint need some special handling, since
        it does not returns the list of objects, but a
        list of routes with a list of buses inside.

        @return: A `Bus` instances list.
        """
        info = api.get(cls.endpoint)

        buses = []
        for route in info:
            for car in route['Linha']['Veiculos']:
                bus = cls(car)
                bus.__route_code__ = route['Linha']['CodigoLinha']
                buses.append(bus)

        return buses

    @classmethod
    def search(cls, *args):
        """
        **Not implemented for buses.**
        """
        raise NotImplemented('Busca não implementada para veiculos')

    def __repr__(self):
        return u'<Bus {0} - {1} {2}>'.format(
            self.code, self.route.code, self.route.description)

    @classmethod
    def nearest(cls, lat, long, **kwargs):
        """
        Search for the nearest buses from `lat` and `long`
        params.

        You should specify the buses to search, default is
        `Buses.all()`.

        @param lat: A float coercible value of latitude (eg.: -5.065533).
        @param long: A float coercible value of longitude (eg.: -42.065533).

        keywords params:
            buses:
                A list of `Stop` instance.
            route:
                A `Route` instance.

        @return: A tuple with a `Bus` object and a `Distance`
            object (see geopy.distance).
        """
        if kwargs.get('buses', False):
            buses = kwargs['buses']
        elif kwargs.get('route', False):
            buses = kwargs['route'].get_buses()
        else:
            buses = cls.all()

        dists = map(lambda bus: distance(
                # Avoid using cached location, to avoid more requests.
                (bus.__lat__, bus.__long__),
                (lat, long)
            ), buses)

        return min(zip(dists, buses))[::-1]

    @property
    @timestampcache(30)
    def lat(self):
        """
        Retrieves the bus's latitude as a `str`.

        @return: a `float` coercible `str`
        """
        self.update()
        return self.__lat__

    @property
    @timestampcache(30)
    def long(self):
        """
        Retrieves the bus's longitude as a `str`.

        @return: a `float` coercible `str`
        """
        self.update()
        return self.__long__
