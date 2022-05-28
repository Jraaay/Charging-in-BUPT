from email.policy import default
from sqlalchemy import TEXT, Boolean, Column, Enum, Index, Integer, String, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from chargingInBupt.config import CONFIG

# 创建对象的基类:
Base = declarative_base()

# 定义User对象:


class User(Base):
    # 表的名字:
    __tablename__ = 'user'

    # 表的结构:
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(TEXT)
    password = Column(TEXT)
    admin = Column(Boolean, default=False)


class Charger(Base):
    # 表的名字:
    __tablename__ = 'charger'

    # 表的结构:
    id = Column(String(20), primary_key=True)
    charger_status = Column(Enum('MAINTAINING', 'SHUTDOWN', 'UNAVAILABLE'))


class ChargeRecord(Base):
    # 表的名字:
    __tablename__ = 'charge_record'

    # 表的结构:
    id = Column(String(20), primary_key=True)
    charger_id = Column(String(20))
    user_id = Column(String(20))
    charge_time = Column(TEXT)


# 初始化数据库连接:
engine = create_engine('mysql+mysqlconnector://' + CONFIG['db']['user'] + ':' + CONFIG['db']['password'] +
                       '@' + CONFIG['db']['host'] + ':' + str(CONFIG['db']['port']) + '/' + CONFIG['db']['db'], echo=False)
# 创建DBSession类型:
session = sessionmaker(bind=engine)()

# Base.metadata.drop_all(engine)
# Base.metadata.create_all(engine)
