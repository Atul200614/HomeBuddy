# PyMySQL setup for native MySQL support on Windows
try:
    import pymysql
    pymysql.install_as_MySQLdb()
except ImportError:
    pass

# Python 3.15 compatibility patch for django.template.context.BaseContext.__copy__
try:
    import copy
    from django.template.context import BaseContext

    def _fixed_copy(self):
        obj = object.__new__(self.__class__)
        obj.__dict__.update(self.__dict__)
        obj.dicts = self.dicts[:]
        return obj

    BaseContext.__copy__ = _fixed_copy
except Exception:
    pass
