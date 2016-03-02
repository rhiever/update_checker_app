from collections import Counter

from flask import abort, jsonify, request, url_for

from . import APP
from .helpers import (get_current_version, normalize, record_check,
                      versions_table)
from .models import Installation, Package, PythonVersion


ALLOWED_PACKAGES = {'datacleaner', 'lazysusan', 'praw', 'redditanalysis', 'tpot', 'xrff2csv'}


@APP.route('/')
def home():
    return "Hello!"


@APP.route('/check', methods=['PUT'])
def check():
    if 'python-requests' not in request.headers.get('User-Agent', ''):
        abort(403)
    required = set(('package_name', 'package_version', 'platform',
                   'python_version'))

    if not request.json or not required.issubset(request.json):
        abort(400)

    package_name = normalize(request.json['package_name'])
    if package_name not in ALLOWED_PACKAGES:
        abort(400)

    package_version = request.json['package_version'].strip()
    platform = normalize(request.json['platform'])
    python_version = normalize(request.json['python_version'])
    if not (package_version and platform and python_version):
        abort(400)

    record_check(package_name, package_version, platform, python_version,
                 request.remote_addr)
    return jsonify(get_current_version(package_name))


@APP.route('/list')
def list():
    retval = '<h3>Packages</h3>\n<ul>\n'
    packages = Counter(x.package_name for x in Package.query.all())
    for package, count in sorted(packages.items()):
        retval += ('  <li><a href="{2}">{0}</a> ({1} versions)</li>\n'
                   .format(package, count, url_for('package_info',
                                                   package_name=package)))
    return retval + '</ul>\n<p><a href="/python">Python Versions</a></p>\n'


@APP.route('/p/<package_name>')
def package_info(package_name):
    packages = Package.query.filter_by(package_name=package_name).all()
    by_id = {x.id: x for x in packages}
    results = Installation.recent_counts(Installation.package_id, by_id.keys())

    versions = [str(by_id[x[0]]) for x in results]
    unique_counts = [x[1] for x in results]
    total_counts = [x[2] for x in results]

    table = versions_table(versions, unique_counts, total_counts)
    return '<h3>Versions from the last 24 hours</h3>\n{0}'.format(table)


@APP.route('/python')
def python_versions():
    pythons = PythonVersion.query.all()
    by_id = {x.id: x for x in pythons}
    results = Installation.recent_counts(Installation.python_id, by_id.keys())

    versions = [str(by_id[x[0]]) for x in results]
    unique_counts = [x[1] for x in results]
    total_counts = [x[2] for x in results]

    table = versions_table(versions, unique_counts, total_counts)
    return '<h3>Versions from the last 24 hours</h3>\n{0}'.format(table)
