import sqlalchemy

class EntityManager(sqlalchemy):
    def __init__(self):
        self.engine = sqlalchemy.create_engine(Env().DATABASE_URL, echo=True)

