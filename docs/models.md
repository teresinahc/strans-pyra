# Strans endpoints mapped models.


Provides access to each endpoint of the Inthegra API.
And adds extra features like search for the nearest bus
or stop.

Besides that, the models provides links betweens the
endpoints that the API itself does not provide.

e.g.:

```
>>> Route.search(401)
[<Route 0401 UNIVERSIDADE>, <Route T0401 BOA VISTA/AV.3/CENTRO/PQ ALVORADA/MUTIRAO - EXT 01>]
```

## Model

  The model base.

The `Model` class is the base for all other models. You must specify
the `endpoint` of the model and the mapper. The `mapper` is a dictionary
where the keys are the API keys of the object and the values are its
respective attribute name on model.

This mapping is made in order to escape the anti-pattern objects keys
of the Inthegra API. The keys are all in portuguese and CamelCase style.

### Methods

**\_\_eq\_\_(self, other)**

  All objects of the API have the `code` attribute. The mappers
  creates it from something like `Codigo...`. This method allows
  compare two objects of the API, even they are not the same
  object in the memory.

  Parameter | Description
  --- | ---
  other | A instance of the same type of `self`.

  **return**: Boolean, if this is equal to `other`.

**\_\_init\_\_(self, obj=None)**

  constructor

  Parameter | Description
  --- | ---
  obj | The object returned by the Inthegra API, as described in the mapper object.

**to_python(self)**

  Maps the Inthegra's endpoint object to Python attributes of the `mapper`.

  Note: It does not make casting yet.

**update(self)**

  Retrieves all the elements of the endpoint, search
  for the current one and updates.

**all(cls)**

  All the endpoints of the API returns all of its elements if
  called without params. This method returns all elements of
  a endpoint as objects.

  **return**: A list of instances of the model.

**filter(cls, func)**

  Applies a filter through `filter` Python function,
  using `func` and all the objects of the endpoint.

  Parameter | Description
  --- | ---
  func | A callable what returns boolean coercible value, receiving a `cls` instance.

  return: A list of `cls` instances.

**search(cls, pattern)**

  This method is a wrapper to the `busca` param of
  some endpoints of the API.

  Parameter | Description    
  --- | ---
  pattern | Something serializable by `requests` lib. You can use the code of some object or something like a neighborhood for `Route`.

  **return**: A list of instances of `cls`.

## Route

  Provides a model to access the endpoint `linhas`.

  Attribute | Description
  --- | ---
  code | A unique `str` that identifies the route (e.g.: '0401').
  description | A `str` route description (e.g.: 'UNIVERSIDADE').
  source | A `str` that identifies the route's start point.
  dest | A `str` that identifies the route's end point.
  circular| A boolean, if the route returns to the source.

### Methods

**get_buses(self)**

  Return all the buses of a route, using `veiculosLinha` endpoint.

  This method is cached for 30 seconds, for the object from it was
  called.

  **return**: A list of `Bus` instances.

**get_stops(self)**

  Return all the stops of a route, using `paradasLinha` endpoint.

  This method is permanently cached when this is called for a
  object, and it's cached for that object.

  return: A list of `Stop` instances.

**get_route(cls, route)**

  Return the first route that `code` matches exactly with `route`.

  You can use a int with `route` too:
```python
>>> Route.get_route(401)
<Route 0401 UNIVERSIDADE>
```
   Parameter | Description
   --- | ---
   route|  A int or a str coercible value.

   **return**: A `Route` isinstance.

   Raises `RouteNotFoundError` if no route was found.


## Stop

  Model for `paradas` endpoint.

  Attribute | Description
  --- | ---
  code | A unique `int` that identifies the stop.
  escription | A `str` description.
  address | A `str`, the stop's address location.
  lat | A `float` coercible `str`.
  long | A `float` coercible `str`.


### Methods

**get_routes(self)**

  Returns all the routes that have this stop.

  >Warning: Don't use that if it's not required.
        This method is too slow and several requests.
        However, it's useful to find what bus should
        be got.

  **return**: A list of `Route` instances.


**nearest(cls, lat, long, **kwargs)**

  Search for the nearest stop from `lat` and `long`
  params.

  You should specify the stops to search, default is
  `Stop.all()`.

  Parameter | Description
  --- | ---
  lat | A float coercible value of latitude (eg.: -5.065533).
  long | A float coercible value of longitude (eg.: -42.065533).


   Keyword arg | Description
   --- | ---
   stops | A list of `Stop` instance.
   route | A `Route` instance.

   **return**: A tuple with a `Stop` object and a `Distance`
    object (see geopy.distance).

    ## Bus

    Model for `veiculos` endpoint.

    ### Attributes
    Attribute | Description
    --- | ---
    code | a `int` unique identify.
    lat | a `float` coercible `str` for latitude.
    long | a `float` coercible `str` for longitude.
    hour | the last location update of the bus.

    ### Methods

    **all(cls)**

      Retrieves all buses from the API.

      This endpoint need some special handling, since
      it does not returns the list of objects, but a
      list of routes with a list of buses inside.

      **return**: A `Bus` instances list.

    **nearest(cls, lat, long, \*\*kwargs)**

      Search for the nearest buses from `lat` and `long`
      params.

      You should specify the buses to search, default is `Buses.all()`.

      Parameter | Description
      --- | ---
      lat | A float coercible value of latitude (eg.: -5.065533).
      long | A float coercible value of longitude (eg.: -42.065533).

      **Keywords params**

      Param | Description
      --- | ---  
      buses | A list of `Stop` instance.
      route | A `Route` instance.

      **return**: A tuple with a `Bus` object and a `Distance` object (see geopy.distance).

    **search(cls, *args)**

      > Not implemented for buses.
