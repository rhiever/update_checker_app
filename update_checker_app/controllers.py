from collections import Counter
from flask import abort, jsonify, request, url_for
from . import APP
from .helpers import get_current_version
from .models import IPAddr, Installation, Package, Platform, PythonVersion, db


ALLOWED_PACKAGES = {'lazysuzan', 'praw'}


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
    package_version = request.json['package_version']
    platform = request.json['platform']
    python_version = request.json['python_version']

    if package_name not in ALLOWED_PACKAGES:
        abort(400)

    ipaddr = IPAddr.fetch_or_create(value=request.remote_addr)
    package = Package.fetch_or_create(package_name=package_name,
                                      package_version=package_version)
    platform = Platform.fetch_or_create(value=platform)
    python_version = PythonVersion.fetch_or_create(value=python_version)

    rows = Installation.query.filter_by(
        day=db.func.Date(db.func.now()), ipaddr=ipaddr, package=package,
        platform=platform, python_version=python_version).update(
        {Installation.count: Installation.count + 1},
        synchronize_session=False)
    if not rows:
        installation = Installation(count=1, ipaddr=ipaddr, package=package,
                                    platform=platform,
                                    python_version=python_version)
        db.session.add(installation)
    db.session.commit()
    return jsonify(get_current_version(package_name))


@APP.route('/list')
def list():
    retval = '<ul>\n'
    packages = Counter(x.package_name for x in Package.query.all())
    for package, count in sorted(packages.items()):
        retval += ('  <li><a href="{2}">{0}</a> ({1} versions)</li>\n'
                   .format(package, count, url_for('package_info',
                                                   package_name=package)))
    return retval + '<ul>\n'


@APP.route('/p/<package_name>')
def package_info(package_name):
    packages = Package.query.filter_by(package_name=package_name).all()
    if not packages:
        return 'We have no records for package `{0}`'.format(package_name)
    retval = '<h1>{0} versions</h1>\n<ul>\n'.format(package_name)
    for package in sorted(packages, reverse=True):
        retval += ('<li><a href="{0}">{1}</a></li>'
                   .format(url_for('version_info', package_name=package_name,
                                   package_id=package.id),
                           package.package_version))
    return retval + '</ul>\n'


@APP.route('/p/<package_name>/<package_id>')
def version_info(package_name, package_id):
    def disp(x):
        return x if x else ''

    package = Package.query.filter_by(id=package_id).first()
    if not package:
        return 'We have no records for package `{0}`'.format(package_id)

    total_checks = (Installation.query.filter_by(package_id=package_id)
                    .order_by(Installation.created_at).all())
    unique_checks = set(x.ipaddr for x in total_checks)
    by_date = [0]
    date_idx = 0
    cur_date = total_checks[0].created_at.date()
    for item in total_checks:
        if item.created_at.date() != cur_date:
            for _ in range((item.created_at.date() - cur_date).days):
                date_idx += 1
                by_date.append(0)
            cur_date = item.created_at.date()
        else:
            by_date[date_idx] += 1

    retval = '<h1>{0} {1}</h1>\n'.format(package_name, package.package_version)
    retval += '<p>Checks: {0}, {1} unique</p>\n'.format(len(total_checks),
                                                        len(unique_checks))
    retval += '<p>First: {0}</p>\n'.format(total_checks[0].created_at)
    retval += '<p>Last: {0}</p>\n'.format(total_checks[-1].created_at)
    retval += '<pre>\n'
    COLUMNS = 7
    for iteration in range(len(by_date) / COLUMNS + 1):
        start = iteration * COLUMNS
        end = min(len(by_date), (iteration + 1) * COLUMNS)
        retval += ' '.join('{0:4}'.format(x) for x in range(start, end))
        retval += '\n'
        retval += ' '.join('{0:4}'.format(disp(x)) for x in by_date[start:end])
        retval += '\n\n'
    return retval + '\n<pre>'
