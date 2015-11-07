"""Defines various one-off helpers for the package."""
from functools import wraps
from time import time
import requests


def configure_logging(app):
    """Send ERROR log to ADMINS emails."""
    ADMINS = ['bbzbryce@gmail.com']
    if not app.debug:
        import logging
        from logging.handlers import SMTPHandler
        mail_handler = SMTPHandler(
            '127.0.0.1', 'server-error@update_checker.bryceboe.com',
            ADMINS, 'UpdateChecker Failed')
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)


def package_cache(function):
    """Memoize the wrapped function."""
    CACHE_TIME = 600
    stored = {}

    @wraps(function)
    def wrapped(package_name):
        now = time()
        if package_name in stored:
            updated, data = stored[package_name]
            if now < updated + CACHE_TIME:
                return data
        data = function(package_name)
        stored[package_name] = (now, data)
        return data
    return wrapped


@package_cache
def get_current_version(package):
    """Return information about the current version of package."""
    r = requests.get('http://pypi.python.org/pypi/{0}/json'.format(package))
    if r.status_code != 200:
        return {'success': False}
    upload_time = None
    json_data = r.json()
    for file_info in json_data['urls']:
        if file_info['packagetype'] == 'sdist':
            upload_time = file_info['upload_time']
    return {'success': True, 'data': {'upload_time': upload_time,
                                      'version': json_data['info']['version']}}
