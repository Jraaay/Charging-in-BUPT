import datetime
from decimal import Decimal
import math
from chargingInBupt.Timer import Timer

from sanic import Sanic, json
from sanic.response import text

from chargingInBupt.auth import authorized, generate_token, authorized_admin, get_username
from chargingInBupt.orm import ChargeArea, ChargeWaitArea, User, session, ChargeRequest, WaitQueue, Charger, WaitArea, ChargeRecord
from chargingInBupt.json_validate import json_validate
from chargingInBupt.json_schema import *
from chargingInBupt.config import CONFIG
from chargingInBupt.schedule import schedule
from sqlalchemy import and_, func

from sanic.log import *
import logging
from sanic import response
from sanic.exceptions import *
# 指定日志的文件名字，记录的日志记录在那个文件中
logging.basicConfig(filename="access.log", format='%(asctime)s %(filename)s %(levelname)s %(message)s',)

app = Sanic("Charging_in_BUPT", configure_logging=LOGGING_CONFIG_DEFAULTS)

@app.exception(SanicException)
async def err404(request, exception):
    error_logger.warning("SanicException: {0} {1}".format(request.url,exception))
    return response.json({"code": -1, "messages": exception.args[0]})


@app.exception(ServerError)
async def ignore_sanic_5001(request, exception):
    error_logger.warning()
    return response.json({"code": -1, "messages": exception.args[0]})

@app.middleware("request")
async def log_uri(request):
    # Simple middleware to log the URI endpoint that was called
    logger.info("URI called: {0}".format(request.url))

@app.middleware("request")
async def log_request(request):
    # Simple middleware to log the request
    logger.info("Request: {0}".format(request.json))

@app.middleware("response")
async def log_response(request, response):
    # Simple middleware to log the response
    logger.info("Response: {0}".format(response.body))






@app.post('/api/login')
@json_validate(login_json_schema)
async def login(request):
    print(request)
    if request.json:
        username = request.json.get('username')
        password = request.json.get('password')
        user = session.query(User).filter(User.username == username).first()
        if user is None:
            return json({
                "code": -1,
                "message": "Invalid username or password"
            })
        if user.password != password:
            return json({
                "code": -1,
                "message": "Invalid username or password"
            })
        token = generate_token(username, user.admin)
        return json({
            "code": 0,
            "message": "Success",
            "data": {
                "token": token,
                "is_admin": user.admin,
            }
        })
    else:
        return json({
            "code": -1,
            "message": "Invalid request"
        })


@app.post('/api/user/register')
@json_validate(register_json_schema)
async def register(request):
    username = request.json.get('username')
    password = request.json.get('password')
    re_password = request.json.get('re_password')
    if password != re_password:
        return json({
            "code": -1,
            "message": "Password not match"
        })
    user = session.query(User).filter(User.username == username).first()
    if user is not None:
        return json({
            "code": -1,
            "message": "Username already exists"
        })
    user = User(username=username, password=password)
    session.add(user)
    session.commit()
    return json({"code": 0, "message": "Success"})


@app.get('/api/test')
@authorized()
async def hello_world(request):
    return text("Hello, world.")


@app.get('/api/test_admin')
@authorized_admin()
async def hello_world(request):
    return text("Hello, admin.")


@app.post('/api/user/submit_charging_request')
@json_validate(submit_charging_request_json_schema)
@authorized()
async def submit_charging_request(request):
    user = session.query(User).filter(
        User.username == get_username(request)).first()
    charge_mode = request.json.get('charge_mode')
    require_amount = request.json.get('require_amount')
    battery_size = request.json.get('battery_size')
    # TODO(1): 处理，获取 charge_id
    # 判断是否不在充电状态:没有充电记录或者不存在待充电请求则代表不在充电状态
    record = session.query(ChargeRequest).filter(
        ChargeRequest.user_id == user.id).first()
    undo_record = session.query(ChargeRequest).filter(
        and_(ChargeRequest.user_id == user.id, ChargeRequest.state != 0)).first()
    charge_time = None
    if record is None or undo_record is None:
        # 插入对应队列
        if session.query(WaitQueue).filter(WaitQueue.state == 1).count() < CONFIG['cfg']['N']:
            # 生成charge_id,加入队列
            his_front_cars = session.query(ChargeRequest).filter(
                and_(ChargeRequest.charge_mode == charge_mode, ChargeRequest.state != 0)).count()
            if his_front_cars == 0:
                charge_id = charge_mode + '1'
            else:
                res_raw = session.query(ChargeRequest).filter(
                    and_(ChargeRequest.charge_mode == charge_mode, ChargeRequest.state != 0)).all()
                res = max([int(i.charge_id[1:]) for i in res_raw])
                charge_id = charge_mode + str(res + 1)

            if charge_mode == "F":
                charge_time = Decimal(require_amount) / \
                    CONFIG['cfg']['F_power'] * 60
            elif charge_mode == "T":
                charge_time = Decimal(require_amount) / \
                    CONFIG['cfg']['T_power'] * 60
            # 生成充电请求，插入数据库
            timer = Timer()
            submit_time = timer.get_cur_timestamp()
            charge_request = ChargeRequest(state=1, user_id=user.id, charge_mode=charge_mode,
                                           require_amount=float(require_amount), charge_time=charge_time,
                                           battery_size=float(battery_size), charge_id=charge_id,
                                           request_submit_time=submit_time)
            session.add(charge_request)
            session.commit()
            # WaitArea 等候区队列处理
            session.add(
                WaitArea(request_id=charge_request.id, type=charge_mode))
            session.commit()

            session.add(WaitQueue(type=charge_mode,
                        state=1, charge_id=charge_id))
            session.commit()
            success = True
            error_msg = None
            # 如果等待区不为空要调度:似乎只需要调度程序对WaitQueue中state=1的记录不断进行调度即可
            schedule(2, charge_request.id)
        else:
            success = False
            error_msg = "请求失败，等候区已满。"
            charge_id = None
    else:
        success = False
        error_msg = "请求失败，还有待完成充电请求。"
        charge_id = None
    if success:
        return json({
            "code": 0,
            "message": "Success",
            "data": {
                "charge_id": charge_id
            }
        })
    else:
        return json({
            "code": -1,
            "message": error_msg
        })


@app.post('/api/user/edit_charging_request')
@json_validate(edit_charging_request_json_schema)
@authorized()
async def edit_charging_request(request):
    user = session.query(User).filter(
        User.username == get_username(request)).first()
    charge_mode = request.json.get('charge_mode')
    require_amount = request.json.get('require_amount')
    # TODO(1): 处理，修改充电请求
    # 判断是否可以修改
    record = session.query(ChargeRequest).filter(
        and_(ChargeRequest.user_id == user.id, ChargeRequest.state == 1)).first()
    # 存在还在等候区的
    if record is not None:
        # 如果充电模式有修改则放到队列最后
        charge_id = record.charge_id
        if record.charge_mode != charge_mode:
            # WaitArea 等候区相关处理
            session.query(WaitArea).filter(
                WaitArea.request_id == record.id).delete()
            session.add(WaitArea(request_id=record.id,
                        type=charge_mode))
            session.commit()

            # 生成charge_id,加入队列
            his_front_cars = session.query(WaitQueue).filter(
                WaitQueue.type == charge_mode).count()
            if his_front_cars == 0:
                charge_id = charge_mode + '1'
            else:
                res_raw = session.query(ChargeRequest).filter(
                    ChargeRequest.charge_mode == charge_mode).all()
                res = max([int(i.charge_id[1:]) for i in res_raw])
                charge_id = charge_mode + str(res + 1)
            session.query(WaitQueue).filter(WaitQueue.charge_id == record.charge_id).update({
                "charge_id": charge_id,
                "type": charge_mode
            })
        # 修改后数据写入数据库
        session.query(ChargeRequest).filter(ChargeRequest.id == record.id).update({
            "charge_mode": charge_mode,
            "require_amount": require_amount,
            "charge_id": charge_id
        })
        session.commit()
        success = True
        error_msg = None
    else:
        success = False
        error_msg = "修改失败，车辆不在等候区。"
    if success:
        return json({
            "code": 0,
            "message": "Success"
        })
    else:
        return json({
            "code": -1,
            "message": error_msg
        })


@app.get('/api/user/end_charging_request')
@authorized()
async def end_charging_request(request):
    user = session.query(User).filter(
        User.username == get_username(request)).first()
    # TODO(2): 处理，取消充电请求
    # question：用户的最后一个请求一定是最新的要取消的请求吗？
    request = session.query(ChargeRequest).filter(
        ChargeRequest.user_id == user.id).order_by(ChargeRequest.id.desc()).first()
    if request is None:
        success = False
        error_msg = "该用户没有充电请求"
    else:
        # 1.生成详单
        # 生成详单前面部分
        timer = Timer()
        create_time = timer.get_cur_format_time()  # 用内置的timer类获取格式化模拟时间字符串
        now = datetime.datetime.strptime(
            create_time, "%Y-%m-%d %H:%M:%S")  # 把格式化字符串转换为datetime类以进行计算
        # "order_id": "20220101000001",
        order_id = now.strftime("%Y%m%d") + '%06d' % request.id
        record_id = str(session.query(ChargeRecord).count() + 1)

        # 如果当前不在充电:直接生成充电详单
        if request.state != 3:
            charge_record = ChargeRecord(id=record_id, order_id=order_id, create_time=create_time,
                                         charged_amount='%.2f' % 0, charged_time='%.2f' % 0, begin_time='%.2f' % 0,
                                         end_time='%.2f' % 0, charging_cost='%.2f' % 0, service_cost='%.2f' % 0,
                                         total_cost='%.2f' % 0, pile_id=request.charge_pile_id, user_id=user.id
                                         )
            session.add(charge_record)
            session.commit()

        # 如果当前正在充电，计算后再创建充电详单 question：算法尚未测试
        else:
            begin_time = datetime.datetime.fromtimestamp(request.start_time)
            end_time = now
            charged_time = (end_time - begin_time).seconds  # 充电时长

            if request.charge_mode == "F":
                rate = 30
            else:
                rate = 10
            charged_amount = float('%0.2f' % (
                charged_time / 3600 * rate))  # 充电量
            service_cost = float('%0.2f' %
                                 (0.8 * float(charged_amount)))  # 服务费用
            # 计算充电费用：将一天分成6个时间区域，只考虑24h内充完电的情况
            # 07：00 - 10：00  1  平时  0.7元/度
            # 10：00 - 15：00  2  峰时  1.0元/度
            # 15：00 - 18：00  3  平时  0.7元/度
            # 18：00 - 21：00  4  峰时  1.0元/度
            # 21：00 - 23：00  5  平时  0.7元/度
            # 23：00 - 07：00  6  谷时  0.4元/度
            clocks = [7, 10, 15, 18, 21, 23, 7]
            fees = [0.7, 1.0, 0.7, 1.0, 0.7, 0.4]
            # 判断开始时间和结束时间的 时间区域
            for i in range(len(clocks)):
                if clocks[i] <= begin_time.hour < clocks[(i + 1) % len(clocks)] or i == 5:
                    begin_time_zone = i + 1
                if clocks[i] <= end_time.hour < clocks[(i + 1) % len(clocks)] or i == 5:
                    end_time_zone = i + 1
            # 如果开始和结束的时间区域相同
            if begin_time_zone == end_time_zone:
                charging_cost = float('%.2f' % (
                    charged_amount * fees[begin_time_zone - 1]))  # 充电费用
            else:
                # 分别计算开始时间到临界值的时间，结束时间到临界值的时间。单位为秒
                diff_time1 = (clocks[begin_time_zone + 1] - begin_time.hour - 1) * 3600 + \
                             (60 - begin_time.minute) * \
                    60 + 60 - begin_time.second
                diff_time2 = (
                    end_time.hour - clocks[end_time_zone]) * 3600 + end_time.minute * 60 + end_time.second
                zones = []  # 要计算的时间区域。①如果开始区域为2，结束为5，得到2、3、4、5；②如果开始为5，结束为2，得到5、6、1、2
                if begin_time_zone < end_time_zone:
                    for i in range(begin_time_zone, end_time_zone+1):
                        zones.append(i)
                else:
                    for i in range(begin_time_zone, 7):
                        zones.append(i)
                    for i in range(1, end_time_zone):
                        zones.append(i)
                # 对覆盖的所有时间区域进行计算
                for i in zones:
                    if i == begin_time_zone:
                        charging_cost = diff_time1 / 3600 * \
                            rate * fees[begin_time_zone - 1]
                    elif i == end_time_zone:
                        charging_cost += diff_time2 / 3600 * \
                            rate * fees[begin_time_zone - 1]
                    else:
                        charging_cost += (clocks[i + 1] - clocks[i]) * \
                            rate * fees[begin_time_zone - 1]

            charging_cost = float('%.2f' % charging_cost)  # 充电费用
            total_cost = service_cost + charging_cost  # 总费用
            # 添加充电详单
            charge_record = ChargeRecord(id=record_id, order_id=order_id, create_time=create_time,
                                         charged_amount=charged_amount, charged_time=charged_time,
                                         begin_time=begin_time.strftime(
                                             "%Y-%m-%d %H:%M:%S"),
                                         end_time=end_time.strftime(
                                             "%Y-%m-%d %H:%M:%S"),
                                         charging_cost=charging_cost, service_cost=service_cost,
                                         total_cost=total_cost, pile_id=request.charge_pile_id, user_id=user.id
                                         )
            session.add(charge_record)
            session.commit()

            # 更新充电桩信息
            charger = session.query(Charger).filter(
                Charger.id == request.charge_pile_id).first()
            charger.cumulative_charging_time += charged_time
            charger.cumulative_charging_amount = '%.2f' % (
                float(charger.cumulative_charging_amount) + charged_amount)
            charger.cumulative_usage_times += 1
            # 重新写入
            session.query(Charger).filter(Charger.id == request.charge_pile_id).update({
                "cumulative_usage_times": charger.cumulative_usage_times,
                "cumulative_charging_time": charger.cumulative_charging_time,
                "cumulative_charging_amount": charger.cumulative_charging_amount
            })
            session.commit()
        success = True

        # 3.*******触发调度*******
        schedule(1, request.id)

        # 2.更新request状态
        session.query(ChargeRequest).filter(ChargeRequest.id == request.id).update({
            "state": 0
        })

        # remove
        session.query(WaitArea).filter(
            WaitArea.request_id == request.id).delete()
        session.query(WaitQueue).filter(
            WaitQueue.charge_id == request.charge_id).delete()
        session.query(ChargeArea).filter(
            ChargeArea.request_id == request.id).delete()
        session.query(ChargeWaitArea).filter(
            ChargeWaitArea.request_id == request.id).delete()

        session.commit()

    if success:
        return json({
            "code": 0,
            "message": "Success"
        })
    else:
        return json({
            "code": -1,
            "message": error_msg
        })


@app.get('/api/user/query_order_detail')
@authorized()
async def query_order_detail(request):
    user = session.query(User).filter(
        User.username == get_username(request)).first()
    # TODO(2): 处理，获取该用户所有充电详单  √
    order_list = []
    # 读取数据库
    for record in session.query(ChargeRecord).filter(ChargeRecord.user_id == user.id):
        order_list.append({
            "order_id": record.order_id,
            "create_time": record.create_time,
            "charged_amount": record.charged_amount,
            "charged_time": record.charged_time,
            "begin_time": record.begin_time,
            "end_time": record.end_time,
            "charging_cost": record.charging_cost,
            "service_cost": record.service_cost,
            "total_cost": record.total_cost,
            "pile_id": record.pile_id
        })
    success = True
    error_msg = ""

    if success:
        return json({
            "code": 0,
            "message": "Success",
            "data": order_list
        })
    else:
        return json({
            "code": -1,
            "message": error_msg
        })


@app.get('/api/user/preview_queue')
@authorized()
async def preview_queue(request):
    user = session.query(User).filter(
        User.username == get_username(request)).first()
    # TODO(1): 处理，获取排队详情
    # 读取数据库
    record = session.query(ChargeRequest).filter(
        and_(ChargeRequest.user_id == user.id, ChargeRequest.state != 0)).first()
    # 若存在还未结束的充电请求
    if record is not None:
        charge_id = record.charge_id
        info = ['NOTCHARGING ', "WAITINGSTAGE1", "WAITINGSTAGE2",
                "CHARGING", 'CHANGEMODEREQUEUE', 'FAULTREQUEUE']
        cur_state = info[record.state]
        if record.state == 1:
            place = "WAITINGPLACE"
        elif record.state in [2, 3, 5]:
            place = record.charge_pile_id
        else:
            place = None
        # 算前方车辆
        if record.state == 1 or record.state == 4:
            num_wait = session.query(WaitQueue).filter(
                and_(WaitQueue.type == record.charge_mode, WaitQueue.charge_id < record.charge_id)).count()
            num_charge_wait = session.query(ChargeArea).count()

            queue_len = num_wait + num_charge_wait
        elif record.state == 2:
            charge_pile = session.query(Charger).filter(
                Charger.id == record.charge_pile_id).first()
            queue_len = session.query(ChargeArea).filter(
                and_(ChargeArea.pile_id == charge_pile.id, ChargeArea.request_id < record.id)).count()
        elif record.state == 3:
            queue_len = 0
        elif record.state == 5:
            queue_len = 1
        else:
            queue_len = None
    else:
        cur_state = "NOTCHARGING"
        charge_id = None
        queue_len = None
        place = None
    success = True
    error_msg = None
    # success = None
    # error_msg = None
    # charge_id = None
    # queue_len = None
    # cur_state = None
    # place = None
    if success:
        return json({
            "code": 0,
            "message": "Success",
            "data": {
                "charge_id": charge_id,
                "queue_len": queue_len,
                "cur_state": cur_state,
                "place": place
            }
        })
    else:
        return json({
            "code": -1,
            "message": error_msg
        })


@app.get('/api/admin/query_report')
@authorized_admin()
async def query_report(request):
    # TODO(3): 处理，获取充电站的数据报表列表
    timer = Timer()
    # 读取数据库
    charger_list = session.query(Charger).all()
    # 用报表计算结果
    success = None
    error_msg = None
    report_list = None
    if charger_list is None:
        success = False
        error_msg = "没有充电桩"
    else:
        success = True
        report_list = []
        for charger in charger_list:
            pass_seconds_from_start = timer.get_cur_timestamp() - charger.start_time
            charger_fee = session.query(ChargeRecord.id, func.sum(ChargeRecord.charging_cost).label("t_charging_cost"), func.sum(ChargeRecord.service_cost).label(
                "t_service_cost"), func.sum(ChargeRecord.total_cost).label("t_total_cost")).filter(ChargeRecord.id == charger.id).first()
            report_list.append({
                "day": math.ceil(pass_seconds_from_start / 86400),
                "week": math.ceil(pass_seconds_from_start / 604800),
                "month": math.ceil(pass_seconds_from_start / 2592000),
                "pile_id": charger.id,
                "cumulative_usage_times": charger.cumulative_usage_times,
                "cumulative_charging_time": charger.cumulative_charging_time,
                "cumulative_charging_amount": charger.cumulative_charging_amount,
                "cumulative_charging_earning": charger_fee.t_charging_cost,
                "cumulative_service_earning": charger_fee.t_service_cost,
                "cumulative_earning": charger_fee.t_total_cost
            })

    if success:
        return json({
            "code": 0,
            "message": "Success",
            "data": report_list
        })
    else:
        return json({
            "code": -1,
            "message": error_msg
        })


@app.get('/api/admin/query_all_piles_stat')
@authorized_admin()
async def query_all_piles_stat(request):
    # TODO(2): 处理，获取所有充电桩的统计信息  √
    # 读取数据库
    stat_list = []
    for charger in session.query(Charger).order_by(Charger.id):
        stat_list.append({
            "pile_id": charger.id,
            "status": charger.charger_status,
            "cumulative_usage_times": charger.cumulative_usage_times,
            "cumulative_charging_time": charger.cumulative_charging_time,
            "cumulative_charging_amount": charger.cumulative_charging_amount
        })
    if charger is None:
        success = False
        error_msg = "无充电桩"
    else:
        success = True

    if success:
        return json({
            "code": 0,
            "message": "Success",
            "data": stat_list
        })
    else:
        return json({
            "code": -1,
            "message": error_msg
        })


@app.get('/api/admin/query_queue')
@authorized_admin()
async def query_queue(request):
    # TODO(3): 处理，获取目前所有正在排队的用户
    # 读取数据库
    user_in_queue = session.query(ChargeRequest).filter(ChargeRequest.state != 0).join(User, ChargeRequest.user_id == User.id).all()
    timer = Timer()

    success = None
    error_msg = None
    queue_list = None
    if user_in_queue is None:
        success = False
        error_msg = "没有正在排队的用户"
    else:
        success = True
        queue_list = []
        for user in user_in_queue:
            waiting_time = timer.get_cur_timestamp() - user.request_submit_time
            queue_list.append({
                "pile_id": user.charge_pile_id,
                "username": session.query(User.username).filter(User.id == user.user_id).first()[0],
                "battery_size": '{:.2f}'.format(user.battery_size),
                "require_amount": '{:.2f}'.format(user.require_amount),
                "waiting_time": waiting_time
            })

    if success:
        return json({
            "code": 0,
            "message": "Success",
            "data": queue_list
        })
    else:
        return json({
            "code": -1,
            "message": error_msg
        })


@app.post('/api/admin/update_pile')
@json_validate(update_pile_json_schema)
@authorized_admin()
async def update_pile(request):
    pile_id = request.json.get('pile_id')
    status = request.json.get('status')
    success = None
    error_msg = None
    # TODO(3): 处理，更新充电桩状态
    # 写数据库
    charger = session.query(Charger).filter(Charger.id == pile_id).first()
    if charger is None:
        success = False
        error_msg = "充电桩不存在"
    else:
        change = False
        success = True
        if charger.charger_status != status:
            change = True
            if status == 'RUNNING':
                timer = Timer()
                session.query(Charger).filter(Charger.id == pile_id).update(
                    {"charger_status": status, "start_time": timer.get_cur_timestamp()})
            else:
                session.query(Charger).filter(Charger.id == pile_id).update(
                    {"charger_status": status})
        session.commit()
        # 触发调度
        if change and status == 'RUNNING':
            schedule(3, None, charger.type)
        elif change:
            schedule(4, None, err_charger_id=pile_id)

    if success:
        return json({
            "code": 0,
            "message": "Success"
        })
    else:
        return json({
            "code": -1,
            "message": error_msg
        })


@app.get('/api/time')
async def get_time(request):
    timer = Timer()
    return json({
        "code": 0,
        "message": "Success",
        "data": {
            "datetime": timer.get_cur_format_time(),
            "timestamp": timer.get_cur_timestamp(),
            "speed": timer.speed
        }
    })
