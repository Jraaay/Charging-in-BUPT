from email.policy import default
from sqlalchemy import TEXT, Boolean, Column, Enum, Index, Integer, String, create_engine, Float
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from chargingInBupt.config import CONFIG

# 创建对象的基类:
Base = declarative_base()

# 定义User对象:


class User(Base):
    # 表的名字:用户
    __tablename__ = 'user'

    # 表的结构:
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(TEXT)
    password = Column(TEXT)
    admin = Column(Boolean, default=False)


class Charger(Base):
    # 表的名字:充电桩
    __tablename__ = 'charger'

    # 表的结构:
    id = Column(String(20), primary_key=True)
    charger_status = Column(Enum('MAINTAINING', 'SHUTDOWN', 'UNAVAILABLE'))
    #wait_num = Column(Integer, default=0)
    type = Column(String(20))

    charge_list = Column(list)  #充电区
    FastCharingPileNum = Column(Integer,default=2)  #快充电桩数
    TrickleChargingPileNum = Column(Integer,default=3)  #慢充电桩数
    ChargingQueueLen = Column(Integer)  #充电桩排队队列长度
    last_end_time = Column(String(20))  #当前充电桩充电区最后一辆车预计充电结束时间


class WaitArea(Base):
    # 表的名字:
    __tablename__ = 'wait_area'

    # 表的结构:
    type = Column(String(20))  #F/T
    charge_wait_list = Column(list)  #充电区的等候区
    wait_list = Column(list)  #等候区
    WaitingAreaSize = Column(Integer)  #等候区车位容量


class ChargeRecord(Base):
    # 表的名字:充电详单
    __tablename__ = 'charge_record'

    # 表的结构:
    id = Column(String(20), primary_key=True)  # 编号
    create_time = Column(String(20))  # 详单生成时间
    charger_id = Column(String(20))  # 充电桩id
    user_id = Column(String(20))  # 用户id
    charge_amount = Column(Integer(10))  # 充电电量
    charge_time = Column(TEXT)  # 充电时长

    record_id = Column(Integer(20))
    start_time = Column(String(20))  # 启动时间
    end_time = Column(String(20))  # 停止时间

    charge_money = Column(Float)  # 充电费用
    service_money = Column(Float)  # 服务费用
    total_time = Column(Float)  # 总费用
    is_cancel = Column(Boolean)  # 是否被主动取消


class ChargeRequest(Base):
    # 表的名字:充电请求
    __tablename__ = 'charge_request'

    # 表的结构:
    id = Column(String(20), primary_key=True)
    state = Column(Integer, default=0)              # 0代表不在充电，1代表在等候区等待，2代表充电区等待，3代表正在充电，4表示充电模式更改导致的重新排队，5表示充电桩故障需要转移充电桩
    user_id = Column(String(20))
    charge_mode = Column(String(20))
    require_amount = Column(Float)  # 充电量
    charge_time = Column(Float)  # 充电所需时间：充电量除以功率 单位：s
    battery_size = Column(Float)  # 电池电量大小
    charge_id = Column(String(20))  # 等候区排队号
    charge_pile_id = Column(String(20))  # 充电桩编号


class WaitQueue(Base):
    # 表的名字:等候区队列
    __tablename__ = 'wait_queue'

    # 表的结构：
    id = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(Enum('F', 'T'))
    state = Column(Integer)    # 0代表排队号无效，1代表排队号有效（即在排队队列中）
    charge_id = Column(String(20))  # 等候区排队号


# 初始化数据库连接:
engine = create_engine('mysql+mysqlconnector://' + CONFIG['db']['user'] + ':' + CONFIG['db']['password'] +
                       '@' + CONFIG['db']['host'] + ':' + str(CONFIG['db']['port']) + '/' + CONFIG['db']['db'],
                       echo=False)
# 创建DBSession类型:
session = sessionmaker(bind=engine)()

 #Base.metadata.drop_all(engine)
 #Base.metadata.create_all(engine)
