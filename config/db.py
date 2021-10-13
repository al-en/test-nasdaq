from sqlalchemy import create_engine, MetaData
from config.settings import settings

engine = create_engine(settings.SQLALCHEMY_DATABASE_URI)

meta = MetaData()

conn = engine.connect()