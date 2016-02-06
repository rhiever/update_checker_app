from collections import Counter
from flask import abort, jsonify, request, url_for
from . import APP
from .helpers import get_current_version, record_check
from .models import Installation, Package


ALLOWED_PACKAGES = {'lazysusan', 'praw'}


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

    package_name = request.json['package_name']
    if package_name not in ALLOWED_PACKAGES:
        abort(400)

    record_check(package_name, request.json['package_version'],
                 request.json['platform'], request.json['python_version'],
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
    results = Installation.recent_counts(Installation.package_id,
                                         [x.id for x in packages])

    rows = ['<tr><th>Version</th><th>Unique</th><th>Total</th></tr>']
    uniq_sum = total_sum = 0
    for pid, uniq, total in results:
        rows.append('<tr><td>{0}</td><td>{1}</td><td>{2}</td></tr>'
                    .format(str(by_id[pid]), uniq, total))
        uniq_sum += uniq
        total_sum += total

    rows.append('<tr><td>Sum</td><td>{0}</td><td>{1}</td></tr>'
                .format(uniq_sum, total_sum))

    return '<h3>Versions from the last 24 hours</h3>\n<table>\n{0}</table>'\
        .format('\n'.join(rows))


@APP.route('/python')
def python_versions():
    return ''
