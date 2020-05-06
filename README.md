This library provides a simple API to launch Conclave (https://github.com/multiparty/conclave) containers on OpenShift.

To run (in a cluster):

```
gunicorn -b 0.0.0.0:8080 -c config.py -e PYTHONBUFFERED=TRUE wsgi:app
```
