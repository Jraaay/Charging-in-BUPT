from sanic import Sanic, json
from sanic.response import text

from chargingInBupt.auth import authorized, generate_token, authorized_admin, get_username
from chargingInBupt.orm import User, session, ChargeRequest
from chargingInBupt.json_validate import json_validate
from chargingInBupt.json_schema import *
from chargingInBupt.config import CONFIG


app = Sanic("Charging_in_BUPT")
F_wait_list = []
T_wait_list = []


@app.post('/user/login')
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
        token = generate_token(user.id, username)
        return json({
            "code": 0,
            "message": "Success",
            "is_admin": user.admin,
            "data": {
                "token": token
            }
        })
    else:
        return json({
            "code": -1,
            "message": "Invalid request"
        })


@app.post('/user/register')
@json_validate(register_json_schema)
async def register(request):
    username = request.json.get('username')
    password = request.json.get('password')
    re_password = request.json.get('re_password')
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


@app.get('/test')
@authorized()
async def hello_world(request):
    return text("Hello, world.")


@app.get('/test_admin')
@authorized_admin()
async def hello_world(request):
    return text("Hello, admin.")


@app.post('/user/submit_charging_request')
@json_validate(submit_charging_request_json_schema)
@authorized()
async def submit_charging_request(request):
    user = session.query(User).filter(User.username == get_username(request)).first()
    charge_mode = request.json.get('charge_mode')
    require_amount = request.json.get('require_amount')
    battery_size = request.json.get('battery_size')
    # TODO(1): 处理，获取 charge_id
    # 判断是否不在充电状态:没有充电记录或者不存在待充电请求则代表不在充电状态
    record = session.query(ChargeRequest).filter(ChargeRequest.user_id == user.id).first()
    undo_record = session.query(ChargeRequest).filter(ChargeRequest.user_id == user.id and ChargeRequest.state in [0,1,2]).first()
    charge_time = None
    if record is None or undo_record is None:
        # 请求id
        record_num = session.query(ChargeRequest).count()
        request_id = str(record_num + 1)
        # 插入对应队列
        if len(F_wait_list)+len(T_wait_list) < 6:
            if charge_mode == "F":
                F_wait_list.append(request_id)
                charge_time = require_amount/CONFIG['cfg']['F_power']
                charge_id = "F"+str(len(F_wait_list))
            elif charge_mode == "T":
                T_wait_list.append(request_id)
                charge_time = require_amount/CONFIG['cfg']['T_power']
                charge_id = "T"+str(len(T_wait_list))
            else:
                charge_id = None
            # 生成充电请求，插入数据库
            charge_request = ChargeRequest(id=request_id, state=0, user_id=user.id, charge_mode=charge_mode, require_amount=float(require_amount), charge_time=charge_time, battery_size=float(battery_size), charge_id=charge_id)
            session.add(charge_request)
            session.commit()
            success = True
            error_msg = None
            # 如果等待区不为空要调度:似乎只需要调度程序对F_wait_list，T_wait_list不断进行调度即可
            '''
            if charge_mode == "F":
                # 调度函数（充电请求id）:充电请求id:F_wait_list[0]
                pass
            elif charge_mode == "T":
                # 调度函数（充电请求id）:充电请求id:T_wait_list[0]
                pass
            '''
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


@app.post('/user/edit_charging_request')
@json_validate(edit_charging_request_json_schema)
@authorized()
async def edit_charging_request(request):
    user = session.query(User).filter(User.username == get_username(request)).first()
    charge_mode = request.json.get('charge_mode')
    require_amount = request.json.get('require_amount')
    # TODO(1): 处理，修改充电请求
    # 判断是否可以修改
    record = session.query(ChargeRequest).filter(ChargeRequest.user_id == user.id and ChargeRequest.state == 0).first()
    # 存在还在等候区的
    if record is not None:
        # 如果充电模式有修改则放到队列最后
        if record.charge_mode != charge_mode:
            if record.charge_mode == "F":
                F_wait_list.remove(record.id)
                # 让所有排在该请求后面的请求的排队号-1
                for request_id in F_wait_list:
                    session.query(ChargeRequest).filter(ChargeRequest.id == request_id and int(ChargeRequest.charge_id[1:])>int(record.charge_id[1:])).update({
                        "charge_id": "F" + str(int(ChargeRequest.charge_id[1:])-1)
                    })
                charge_id = "F" + str(F_wait_list)
                F_wait_list.append(record.id)
            elif record.charge_mode == "T":
                T_wait_list.remove(record.id)
                # 让所有排在该请求后面的请求的排队号-1
                for request_id in T_wait_list:
                    session.query(ChargeRequest).filter(ChargeRequest.id == request_id and int(ChargeRequest.charge_id[1:])>int(record.charge_id[1:])).update({
                        "charge_id": "F" + str(int(ChargeRequest.charge_id[1:])-1)
                    })
                charge_id = "T" + str(F_wait_list)
                T_wait_list.append(record.id)
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


@app.get('/user/end_charging_request')
@authorized()
async def end_charging_request(request):
    user = session.query(User).filter(User.username == get_username(request)).first()
    # TODO(2): 处理，取消充电请求
    # 生成详单
    # 更新状态
    # 触发调度
    success = None
    error_msg = None
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

@app.get('/user/query_order_detail')
@authorized()
async def query_order_detail(request):
    user = session.query(User).filter(User.username == get_username(request)).first()
    # TODO(2): 处理，获取该用户所有充电详单
    # 读取数据库
    success = None
    error_msg = None
    order_list = None
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

@app.get('/user/preview_queue')
@authorized()
async def preview_queue(request):
    user = session.query(User).filter(User.username == get_username(request)).first()
    # TODO(1): 处理，获取排队详情
    # 读取数据库
    record = session.query(ChargeRequest).filter(ChargeRequest.user_id == user.id and ChargeRequest.state in [0,1,2]).first()
    # 若存在还未结束的充电请求
    if record is not None:
        charge_id = record.charge_id
        info = ["WAITINGSTAGE1","WAITINGSTAGE2","CHARGING"]
        cur_state = info[record.state]
        if record.state == 0:
            place = "WAITINGPLACE"
        elif record.state in [1,2]:
            place = record.charge_pile_id
        else:
            place = None
        # 算前方车辆
        if record.state == 0:
            queue_len = (record.charge_id[1:])
        elif record.state == 1:
            # queue_len = 对应record.charge_pile_id充电桩前面车的数量
            queue_len = None
            pass
        elif record.state == 2:
            queue_len = 0
        else:
            queue_len = None
    else:
        cur_state = "NOTCHARGING"
        charge_id = None
        queue_len = None
        cur_state = None
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

@app.get('/admin/query_report')
@authorized_admin()
async def query_report(request):
    # TODO(3): 处理，获取充电站的数据报表列表
    # 读取数据库
    # 用报表计算结果
    success = None
    error_msg = None
    report_list = None
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

@app.get('/admin/query_all_piles_stat')
@authorized_admin()
async def query_all_piles_stat(request):
    # TODO(2): 处理，获取所有充电桩的统计信息
    # 读取数据库
    success = None
    error_msg = None
    stat_list = None
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

@app.get('/admin/query_queue')
@authorized_admin()
async def query_queue(request):
    # TODO(3): 处理，获取目前所有正在排队的用户
    # 读取数据库
    success = None
    error_msg = None
    queue_list = None
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

@app.post('/admin/update_pile')
@json_validate(update_pile_json_schema)
@authorized_admin()
async def update_pile(request):
    charger_id = request.json.get('charger_id')
    status = request.json.get('status')
    # TODO(3): 处理，更新充电桩状态
    # 写数据库
    # 触发调度
    success = None
    error_msg = None
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
