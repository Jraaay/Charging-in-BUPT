from sanic import Sanic, json
from sanic.response import text

from chargingInBupt.auth import authorized, generate_token, authorized_admin, get_username
from chargingInBupt.orm import User, session
from chargingInBupt.json_validate import json_validate
from chargingInBupt.json_schema import *


app = Sanic("Charging_in_BUPT")


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
    # TODO: 处理，获取 charge_id
    success = None
    error_msg = None
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
    # TODO: 处理，修改充电请求
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

@app.get('/user/end_charging_request')
@authorized()
async def end_charging_request(request):
    user = session.query(User).filter(User.username == get_username(request)).first()
    # TODO: 处理，取消充电请求
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
    # TODO: 处理，获取该用户所有充电详单
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
    # TODO: 处理，获取排队详情
    success = None
    error_msg = None
    charge_id = None
    queue_len = None
    cur_state = None
    place = None
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
    # TODO: 处理，获取充电站的数据报表列表
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
    # TODO: 处理，获取所有充电桩的统计信息
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
    # TODO: 处理，获取目前所有正在排队的用户
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
    # TODO: 处理，更新充电桩状态
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
