# Alternative MySQL driver for Windows
import sys
if sys.platform == 'win32':
    try:
        import pymysql
        pymysql.install_as_MySQLdb()
    except ImportError:
        pass

