This library provides a simple web interface to launch Conclave containers on OpenShift.

To run (in a cluster):

```
gunicorn -b 0.0.0.0:8080 -c config.py -e PYTHONBUFFERED=TRUE wsgi:app
```