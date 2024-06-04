class __ORMException(Exception):
    pass


class ReadOnlyException(__ORMException):
    def __init__(self, message: str = 'This is read-only Entity'):
        super().__init__(message)

class ODBCException(__ORMException):
    def __init__(self, message: str = 'Open Database Connectivity (ODBC) Exception'):
        super().__init__(message)