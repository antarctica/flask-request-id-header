# Flask Request ID Middleware

Python Flask middleware to ensure all requests have a request ID header.

## Purpose

This middleware ensures all request made to a Flask application includes a Request ID header (`X-Request-ID`), 
containing at least one unique value.

[Request IDs](https://theburningmonk.com/2015/05/a-consistent-approach-to-track-correlation-ids-through-microservices/)
or *Correlation IDs* can be used when logging errors and allows users to trace requests through multiple layers such as
load balancers and reverse proxies. The request ID header value may consist of multiple IDs encoded according to 
[RFC 2616](http://www.w3.org/Protocols/rfc2616/rfc2616-sec4.html#sec4.2).

## Installation

This package can be installed using Pip from [PyPi](https://pypi.org/project/flask-request-id-header):

```
$ pip install flask-request-id-header
```

## Usage

This middleware has no required parameters and by default will add a request header to requests where one does not 
already exist, or append a unique value where existing request IDs do not contain at least one UUID (version 4) value.

A minimal application would look like this:

```python
from flask import Flask
from flask_request_id_header.middleware import RequestID

app = Flask(__name__)

RequestID(app)

@app.route('/')
def hello_world():
    return 'hello world'
```

Optionally a Flask config option, `REQUEST_ID_UNIQUE_VALUE_PREFIX`, can be set whereby any request ID beginning with 
this prefix be treated as unique, preventing an additional value being appended.

A minimal application would look like this:

```python
from flask import Flask
from flask_request_id_header.middleware import RequestID

app = Flask(__name__)

app.config['REQUEST_ID_UNIQUE_VALUE_PREFIX'] = 'FOO-'
RequestID(app)

@app.route('/')
def hello_world():
    return 'hello world'
```

### Accessing the request ID

The current request ID can be accessed wherever a request context exists:

```python
from flask import request, has_request_context

if has_request_context():
    print(request.environ.get("HTTP_X_REQUEST_ID"))
```

To access the request ID outside of the current application, it is included in the response (as `X-Request-ID`).

**Note:** Components between the application and the client, such as reverse proxies, may alter or remove this header
value before reaching the client.

### Logging the request ID

Optionally, the current request ID can be included in application logs, where a request context exists.

A minimal application would look like this:

```python
import logging

from flask import Flask, request, has_request_context
from flask.logging import default_handler
from flask_request_id_header.middleware import RequestID

app = Flask(__name__)

app.config['REQUEST_ID_UNIQUE_VALUE_PREFIX'] = 'FOO-'
RequestID(app)

class RequestFormatter(logging.Formatter):
    def format(self, record):
        record.request_id = 'NA'

        if has_request_context():
            record.request_id = request.environ.get("HTTP_X_REQUEST_ID")

        return super().format(record)

formatter = RequestFormatter(
    '[%(asctime)s] [%(levelname)s] [%(request_id)s] %(module)s: %(message)s'
)
default_handler.setFormatter(formatter)

@app.route('/')
def hello_world():
    return 'hello world'
```

## Developing

A docker container ran through Docker Compose is used as a development environment for this project defined . It 
includes development only dependencies listed in `requirements.txt`, a local Flask application in `app.py` and 
[Integration tests](#integration-tests).

Ensure classes and methods are defined within the `flask_request_id_header` package.

Ensure [Integration tests](#integration-tests) are written for any new feature, or changes to existing features.

If you have access to the BAS GitLab instance, pull the Docker image from the BAS Docker Registry:

```shell
$ docker login docker-registry.data.bas.ac.uk
$ docker-compose pull

# To run the local Flask application using the Flask development server
$ docker-compose up

# To start a shell
$ docker-compose run app ash
```

### Code Style

PEP-8 style and formatting guidelines must be used for this project, with the exception of the 80 character line limit.

[Flake8](http://flake8.pycqa.org/) is used to ensure compliance, and is ran on each commit through 
[Continuous Integration](#continuous-integration).

To check compliance locally:

```shell
$ docker-compose run app flake8 . --ignore=E501
```

### Dependencies

Development Python dependencies should be declared in `requirements.txt` to be included in the development environment.

Runtime Python dependencies should be declared in `requirements.txt` and `setup.py` to also be installed as dependencies
of this package in other applications.

All dependencies should be periodically reviewed and update as new versions are released.

```shell
$ docker-compose run app ash
$ pip install [dependency]==
# this will display a list of available versions, add the latest to `requirements.txt` and or `setup.py`
$ exit
$ docker-compose down
$ docker-compose build
```

If you have access to the BAS GitLab instance, push the Docker image to the BAS Docker Registry:

```shell
$ docker login docker-registry.data.bas.ac.uk
$ docker-compose push
```

### Dependency vulnerability scanning

To ensure the security of this API, all dependencies are checked against 
[Snyk](https://app.snyk.io/org/antarctica/project/ef12439f-4d28-45af-81c2-fad464a05184) for vulnerabilities. 

**Warning:** Snyk relies on known vulnerabilities and can't check for issues that are not in it's database. As with all 
security tools, Snyk is an aid for spotting common mistakes, not a guarantee of secure code.

Some vulnerabilities have been ignored in this project, see `.snyk` for definitions and the 
[Dependency exceptions](#dependency-vulnerability-exceptions) section for more information.

Through [Continuous Integration](#continuous-integration), on each commit current dependencies are tested and a snapshot
uploaded to Snyk. This snapshot is then monitored for vulnerabilities.

#### Dependency vulnerability exceptions

This project contains known vulnerabilities that have been ignored for a specific reason.

* [Py-Yaml `yaml.load()` function allows Arbitrary Code Execution](https://snyk.io/vuln/SNYK-PYTHON-PYYAML-42159)
    * currently no known or planned resolution
    * indirect dependency, required through the `bandit` package
    * severity is rated *high*
    * risk judged to be *low* as we don't use the Yaml module in this application
    * ignored for 1 year for re-review

### Static security scanning

To ensure the security of this API, source code is checked against [Bandit](https://github.com/PyCQA/bandit) for issues 
such as not sanitising user inputs or using weak cryptography. 

**Warning:** Bandit is a static analysis tool and can't check for issues that are only be detectable when running the 
application. As with all security tools, Bandit is an aid for spotting common mistakes, not a guarantee of secure code.

Through [Continuous Integration](#continuous-integration), each commit is tested.

To check locally:

```shell
$ docker-compose run app bandit -r .
```

## Testing

### Integration tests

This project uses integration tests to ensure features work as expected and to guard against regressions and 
vulnerabilities.

The Python [UnitTest](https://docs.python.org/3/library/unittest.html) library is used for running tests using Flask's 
test framework. Test cases are defined in files within `tests/` and are automatically loaded when using the 
`test` Flask CLI command included in the local Flask application in the development environment.

Tests are automatically ran on each commit through [Continuous Integration](#continuous-integration).

To run tests manually:

```shell
$ docker-compose run -e FLASK_ENV=testing app flask test
```

To run tests using PyCharm:

* *Run* -> *Edit Configurations*
* *Add New Configuration* -> *Python Tests* -> *Unittests*

In *Configuration* tab:

* Script path: `[absolute path to project]/tests`
* Python interpreter: *Project interpreter* (*app* service in project Docker Compose)
* Working directory: `[absolute path to project]`
* Path mappings: `[absolute path to project]=/usr/src/app`

**Note:** This configuration can be also be used to debug tests (by choosing *debug* instead of *run*).

### Continuous Integration

All commits will trigger a Continuous Integration process using GitLab's CI/CD platform, configured in `.gitlab-ci.yml`.

This process will run the application [Integration tests](#integration-tests).

Pip dependencies are also [checked and monitored for vulnerabilities](#dependency-vulnerability-scanning).

## Distribution
 
Both source and binary versions of the package are build using [SetupTools](https://setuptools.readthedocs.io), which 
can then be published to the [Python package index](https://pypi.org/project/flask-request-id-header/) for use in other 
applications. Package settings are defined in `setup.py`.

This project is built and published to PyPi automatically through [Continuous Deployment](#continuous-deployment).

To build the source and binary artefacts for this project manually:

```shell
$ docker-compose run app ash
# build package to /build, /dist and /flask_reverse_proxy_fix.egg-info
$ python setup.py sdist bdist_wheel
$ exit
$ docker-compose down
```

To publish built artefacts for this project manually to [PyPi testing](https://test.pypi.org):

```shell
$ docker-compose run app ash
$ python -m twine upload --repository-url https://test.pypi.org/legacy/ dist/*
# project then available at: https://test.pypi.org/project/flask-request-id-header/
$ exit
$ docker-compose down
```

To publish manually to [PyPi](https://pypi.org):

```shell
$ docker-compose run app ash
$ python -m twine upload --repository-url https://pypi.org/legacy/ dist/*
# project then available at: https://pypi.org/project/flask-request-id-header/
$ exit
$ docker-compose down
```

### Continuous Deployment

A Continuous Deployment process using GitLab's CI/CD platform is configured in `.gitlab-ci.yml`. This will:

* build the source and binary artefacts for this project
* publish built artefacts for this project to the relevant PyPi repository

This process will deploy changes to [PyPi testing](https://test.pypi.org) on all commits to the *master* branch.

This process will deploy changes to [PyPi](https://pypi.org) on all tagged commits.

## Release procedure

### At release

1. create a `release` branch
2. remove `.dev{ os.getenv('CI_PIPELINE_ID') or None }` from the version parameter in `setup.py` and ensure version 
   is bumped as per semver
3. close release in `CHANGELOG.md`
4. push changes, merge the `release` branch into `master` and tag with version

The project will be built and published to PyPi automatically through [Continuous Deployment](#continuous-deployment).

### After release

1. create a `next-release` branch
2. bump the version parameter in `setup.py` and append `.dev{ os.getenv('CI_PIPELINE_ID') or None }` to signify a     
  pre-release
3. push changes and merge the `next-release` branch into `master`

## Feedback

The maintainer of this project is the BAS Web & Applications Team, they can be contacted at: 
[servicedesk@bas.ac.uk](mailto:servicedesk@bas.ac.uk).

## Issue tracking

This project uses issue tracking, see the 
[Issue tracker](https://gitlab.data.bas.ac.uk/web-apps/flask-middleware/flask-request-id/issues) for more information.

**Note:** Read & write access to this issue tracker is restricted. Contact the project maintainer to request access.

## License

© UK Research and Innovation (UKRI), 2019, British Antarctic Survey.

You may use and re-use this software and associated documentation files free of charge in any format or medium, under 
the terms of the Open Government Licence v3.0.

You may obtain a copy of the Open Government Licence at http://www.nationalarchives.gov.uk/doc/open-government-licence/
