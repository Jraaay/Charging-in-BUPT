from email.policy import default
from sqlalchemy import TEXT, Boolean, Column, Enum, Index, Integer, String, create_engine, Float
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
    wait_num = Column(Integer, default=0)
    type = Column(String(20))


class ChargeRecord(Base):
    # 表的名字:
    __tablename__ = 'charge_record'

    # 表的结构:
    id = Column(String(20), primary_key=True)
    charger_id = Column(String(20))
    user_id = Column(String(20))
    charge_time = Column(TEXT)
   @hqc 
    start_time =  Column(String(20))
    end_time =  Column(String(20))


class ChargeRequest(Base):
    # 表的名字:
    __tablename__ = 'charge_request'

    # 表的结构:
    id = Column(String(20), primary_key=True)
    state = Column(Integer, default=0)              # 0代表等候区等待，1代表在充电桩等待，2代表正在充电，3代表充电完成
    user_id = Column(String(20))
    charge_mode = Column(String(20))
    require_amount = Column(Float)      # 充电量
    charge_time = Column(Float)         # 充电所需时间：充电量除以功率
    battery_size = Column(Float)        # 电池电量大小
    charge_id = Column(String(20))      # 等候区排队号
    charge_pile_id = id = Column(String(20)) # 充电桩编号


# 初始化数据库连接:
engine = create_engine('mysql+mysqlconnector://' + CONFIG['db']['user'] + ':' + CONFIG['db']['password'] +
                       '@' + CONFIG['db']['host'] + ':' + str(CONFIG['db']['port']) + '/' + CONFIG['db']['db'], echo=False)
# 创建DBSession类型:
session = sessionmaker(bind=engine)()

# Base.metadata.drop_all(engine)
# Base.metadata.create_all(engine)
