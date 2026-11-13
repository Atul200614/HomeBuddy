# PyMySQL setup for native MySQL support on Windows
try:
    import pymysql
    pymysql.install_as_MySQLdb()
except ImportError:
    pass
