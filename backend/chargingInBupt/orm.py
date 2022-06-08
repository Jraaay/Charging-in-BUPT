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
    type = Column(String(20))

    FastCharingPileNum = Column(Integer, default=2)  # 快充电桩数
    TrickleChargingPileNum = Column(Integer, default=3)  # 慢充电桩数
    ChargingQueueLen = Column(Integer)  # 充电桩排队队列长度
    last_end_time = Column(String(20))  # 当前充电桩充电区最后一辆车预计充电结束时间

    cumulative_usage_times = Column(Integer, default=0)  # 充电桩累计使用次数
    cumulative_charging_time = Column(Integer, default=0)  # 充电桩累计充电时间
    cumulative_charging_amount = Column(String(20), default="0")  # 充电桩累计充电电量

    start_time = Column(Integer, default=0)  # 充电桩的启动时间


class ChargeArea(Base):
    # 表的名字:
    __tablename__ = 'charge_area'  
    # 表的结构:
    pile_id = Column(String(20))  # 充电桩号
    request_id = Column(String(20), primary_key=True)


class ChargeWaitArea(Base):
    # 表的名字:
    __tablename__ = 'charge_wait_area'  
    # 表的结构:
    type = Column(String(20))  # F/T
    request_id = Column(String(20), primary_key=True)
    WaitingAreaSize = Column(Integer)  # 等候区车位容量


class WaitArea(Base):
    # 表的名字:
    __tablename__ = 'wait_area'

    # 表的结构:
    type = Column(String(20))  # F/T
    request_id = Column(String(20), primary_key=True)
    WaitingAreaSize = Column(Integer)  # 等候区车位容量


class ChargeRecord(Base):
    # 表的名字:充电详单
    __tablename__ = 'charge_record'

    # 表的结构:
    id = Column(String(20), primary_key=True)  # 编号
    order_id = Column(String(20))  # 订单号
    create_time = Column(String(20))  # 详单生成时间
    charged_amount = Column(Float)  # 充电电量
    charged_time = Column(Integer)  # 充电时长
    begin_time = Column(String(20))  # 开始充电时间
    end_time = Column(String(20))  # 结束时间
    charging_cost = Column(Float)  # 充电费用
    service_cost = Column(Float)  # 服务费用
    total_cost = Column(Float)  # 总费用
    pile_id = Column(String(20))  # 充电桩号

    user_id = Column(String(20))  # 用户id


class ChargeRequest(Base):
    # 表的名字:充电请求
    __tablename__ = 'charge_request'

    # 表的结构:
    id = Column(String(20), primary_key=True)
    state = Column(Integer, default=0)  # 0代表不在充电，1代表在等候区等待，2代表充电区等待，3代表正在充电，4表示充电模式更改导致的重新排队，5表示充电桩故障需要转移充电桩
    user_id = Column(String(20))
    charge_mode = Column(String(20))
    require_amount = Column(Float)  # 充电量
    charge_time = Column(Float)  # 充电所需时间：充电量除以功率 单位：s
    start_time = Column(String(20))  # 开始充电时间
    battery_size = Column(Float)  # 电池电量大小
    charge_id = Column(String(20))  # 等候区排队号
    charge_pile_id = Column(String(20))  # 充电桩编号
    request_submit_time = Column(Integer)  # 充电请求提交时间


class WaitQueue(Base):
    # 表的名字:等候区队列
    __tablename__ = 'wait_queue'

    # 表的结构：
    id = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(Enum('F', 'T'))
    state = Column(Integer)  # 0代表排队号无效，1代表排队号有效（即在排队队列中）
    charge_id = Column(String(20))  # 等候区排队号


# 初始化数据库连接:
engine = create_engine('mysql+mysqlconnector://' + CONFIG['db']['user'] + ':' + CONFIG['db']['password'] +
                       '@' + CONFIG['db']['host'] + ':' + str(CONFIG['db']['port']) + '/' + CONFIG['db']['db'],
                       echo=False)
# 创建DBSession类型:
session = sessionmaker(bind=engine)()

Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)
