# Inthegra API Python wrapper.

This is a Python wrapper for the Inthegra API,
designed to be simple, pythonist, safe for human
consumption and provides some features not implemented
in the Inthegra API.

## Installation

```bash
pip install git+https://github.com/teresinahc/strans-pyra
```

## Setup

You need to some configurations from the `settings.template.py`.
Copy that to your application main path as `settings.py` and set
your [application key](https://inthegra.strans.teresina.pi.gov.br/apikey/all),
email and password.

The `settings.template.py` is initialized as:

```python
API_KEY = ''
URL = 'https://api.inthegra.strans.teresina.pi.gov.br/v1'
EMAIL = ''
PASSWORD = ''
USE_CACHE = True

REQUEST_OPTIONS = {

}
```

When you imports `stranspyra` into your project, if `settings.py` is at
the Python path you will automatically logged and the access token
retrieved.

## First run

Put a `settings.py` into some folder and open Python interactive mode
inside it. And search for your favorite bus.

```python
>>> import stranspyra as strans
>>> strans.Route.search('UFPI')
[<Route 0626 HD-SACI-UFPI VIA SHOPPING>, <Route CV03 HD-0626 SACI-UFPI VIA SHOPPING>]
```

More info about `Route` and other models, see [docs/models.md](./docs/models.md).

## Features

* Access whole Inthegra API endpoints
* A model based interface
* Retrieves all stop's buses
* Retrieves the nearest stop to a
  location
* Retrieves the nearest bus to a
  location
* Deep models integration
* Static object caching system
* Timestamp based caching system
* Django-like settings system
* Trace a route between to coordinates

## Requirements

* requests >= 2.8.0
* geopy >= 1.11.0

## Uses

### Accessing routes

```python
>>> import stranspyra as strans
>>> routes = strans.Route.all()
>>> routes[0]
<Route 0001 POTY VELHO B. ESPERANCA VIA ACARAPE>
```

### Searching for a specific route

```python
>>> b401 = strans.Route.get_route(401)
>>> b401
<Route 0401 UNIVERSIDADE>
```

### Tracing route

```python
>>> route = strans.Route.traceroute((-5.0902805,-42.8138435), (-5.0869447,-42.8040027))
>>> route
((<Stop 215 RUA 07 DE SETEMBRO >, Distance(0.165885308859)), (<Stop 199 AV. FREI SERAFIM 6 >, Distance(0.0551390564549)), <Route 0617 HD-PLA. BELA VISTA SHOPPING VIA M.>)
```

### Getting the route's buses

```python
>>> buses = b401.get_buses()
>>> buses
[<Bus 02521 - 0401 UNIVERSIDADE>]
```

### Accessing buses' location

```python
>>> buses[0].lat, buses[0].long
(u'-5.04693500', u'-42.78294300')
```

### Searching for routes

```python
>>> strans.Route.search('Universidade')
[<Route 0401 UNIVERSIDADE>, <Route 0365 UNIVERSIDADE CIRCULAR 2 VIA SHOPPING>,
 <Route 0563 UNIVERSIDADE CIRCULAR I VIA SHOPPING>,
 <Route 0626 HD-SACI-UFPI VIA SHOPPING>,
 <Route 0730 UNIVERSIDADE - CENTRO DUQUE DE CAXIAS>]
```

### Retrieving stops

```python
>>> b401.get_stops()[:2]
[<Stop 2244 PC1 UFPI>, <Stop 875 RUA DIRCE DE OLIVEIRA 4 >]
```

### Retrieving nearest stop

```python
>>> strans.Stop.nearest(-5.056221603326806,-42.79030821362158)
(<Stop 911 Campos Universitario - CCS>, Distance(0.0621590283922))
```

### Retrieving nearest bus

```python
>>> bus = strans.Bus.nearest(-5.056221603326806,-42.79030821362158)
>>> bus
(<Bus 02764 - 0365 UNIVERSIDADE CIRCULAR 2 VIA SHOPPING>, Distance(0.72410974728))
```

## LICENSE

* [MIT](./LICENSE.md)
