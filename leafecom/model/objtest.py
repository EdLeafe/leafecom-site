import model
from sqlalchemy import orm
from sqlalchemy import create_engine

# Create an engine and create all the tables we need
engine = create_engine("mysql://mysql:fil0farn@cloud-webdata/webdata", echo=True)
#engine = create_engine("mysql://mysql:fil0farn@localhost/webdata", echo=True)
model.metadata.bind = engine
model.metadata.create_all()

# Set up the session
sm = orm.sessionmaker(bind=engine, autoflush=True, autocommit=False,
    expire_on_commit=True)
session = orm.scoped_session(sm)

