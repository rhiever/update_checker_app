from pkg_resources import parse_version
from sqlalchemy.ext.declarative import declared_attr
from . import db


class ModelMixin(object):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=db.func.now(), index=True,
                           nullable=False)

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    @classmethod
    def fetch_or_create(cls, **kwargs):
        item = cls.query.filter_by(**kwargs).first()
        if not item:
            item = cls(**kwargs)
        return item


class IPAddr(db.Model, ModelMixin):
    value = db.Column(db.String, nullable=False)


class Installation(db.Model, ModelMixin):
    day = db.Column(db.Date, default=db.func.Date(db.func.now()), index=True,
                    nullable=False)
    count = db.Column(db.Integer, nullable=False)
    ipaddr = db.relationship('IPAddr', backref='installations')
    ipaddr_id = db.Column(db.Integer, db.ForeignKey('ipaddr.id'), index=True,
                          nullable=False)
    package = db.relationship('Package', backref='installations',)
    package_id = db.Column(db.Integer, db.ForeignKey('package.id'), index=True,
                           nullable=False)
    platform = db.relationship('Platform', backref='installations')
    platform_id = db.Column(db.Integer, db.ForeignKey('platform.id'),
                            index=True, nullable=False)
    python_version = db.relationship('PythonVersion', backref='installations')
    python_id = db.Column(db.Integer, db.ForeignKey('pythonversion.id'),
                          index=True, nullable=False)


class Package(db.Model, ModelMixin):
    __table_args__ = (db.UniqueConstraint('package_name', 'package_version'),)
    package_name = db.Column(db.Unicode, nullable=False)
    package_version = db.Column(db.Unicode, nullable=False)

    def __lt__(self, other):
        if self.package_name == other.package_name:
            return parse_version(self.package_version) \
                < parse_version(other.package_version)
        return self.name < other.name


class Platform(db.Model, ModelMixin):
    value = db.Column(db.Unicode, unique=True, nullable=False)


class PythonVersion(db.Model, ModelMixin):
    value = db.Column(db.Unicode, unique=True, nullable=False)
