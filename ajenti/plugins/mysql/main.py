import subprocess

from ajenti.api import *
from ajenti.plugins.configurator.api import ClassConfigEditor
from ajenti.plugins.db_common.api import DBPlugin, Database, User


@plugin
class MySQLClassConfigEditor (ClassConfigEditor):
    title = 'MySQL'
    icon = 'table'

    def init(self):
        self.append(self.ui.inflate('mysql:config'))


@plugin
class MySQLPlugin (DBPlugin):
    default_classconfig = {'user': 'root', 'password': ''}
    classconfig_editor = MySQLClassConfigEditor

    service_name = 'mysql'
    service_buttons = [
        {
            'command': 'reload',
            'text': 'Reload',
            'icon': 'step-forward',
        }
    ]

    def init(self):
        self.title = 'MySQL'
        self.category = 'Software'
        self.icon = 'table'

    def query(self, sql, db=''):
        p = subprocess.Popen([
            'mysql',
            '-u' + self.classconfig['user'],
            '-p' + self.classconfig['password']],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        o, e = p.communicate((('USE %s; ' % db) if db else '') + sql)
        if p.returncode:
            raise Exception(e)
        return filter(None, o.splitlines()[1:])

    def query_sql(self, db, sql):
        r = []
        for l in self.query(sql + ';', db):
            r.append(l.split('\t'))
        return r

    def query_databases(self):
        r = []
        for l in self.query('SHOW DATABASES;'):
            db = Database()
            db.name = l
            r.append(db)
        return r

    def query_drop(self, db):
        self.query("DROP DATABASE `%s`;" % db.name)

    def query_create(self, name):
        self.query("CREATE DATABASE `%s` CHARACTER SET UTF8;" % name)

    def query_users(self):
        r = []
        for l in self.query('USE mysql; SELECT * FROM user;'):
            u = User()
            u.host, u.name = l.split('\t')[:2]
            r.append(u)
        return r

    def query_create_user(self, user):
        self.query("CREATE USER `%s`@`%s` IDENTIFIED BY '%s'" % (user.name, user.host, user.password))

    def query_drop_user(self, user):
        self.query("DROP USER `%s`@`%s`" % (user.name, user.host))