from sqlalchemy import and_
from chargingInBupt.orm import WaitArea, WaitQueue
from chargingInBupt.orm import ChargeRecord, ChargeRequest, Charger, ChargeArea, ChargeWaitArea, WaitArea
from chargingInBupt.orm import session
from chargingInBupt.Timer import Timer


def schedule(schedule_type, request_id, type=None, err_charger_id=None, must_sch=False, error=False):

    if schedule_type is 1:  # 有人完成充电 或者是取消充电
        charge_mode = session.query(ChargeRequest.charge_mode).filter(
            ChargeRequest.id == request_id).first()[0]
        pile_id = session.query(ChargeRequest.charge_pile_id).filter(
            ChargeRequest.id == request_id).first()[0]
        charge_list = session.query(ChargeArea.request_id).filter(
            ChargeArea.pile_id == pile_id).all()
        charge_wait_list = session.query(ChargeWaitArea.request_id).filter(
            ChargeWaitArea.type == charge_mode).all()
        wait_list = session.query(WaitArea.request_id).filter(
            WaitArea.type == charge_mode).all()
        charge_done = session.query(ChargeRequest).filter(
            ChargeRequest.id == request_id).first()

        if charge_done.state == 1 or charge_done.state == 4:
            return

        # 让该充电桩第二辆车充电
        charge_list.remove((str(charge_done.id),))
        # 检查充电区的等候区、等候区，有则叫号进入充电区
        if len(charge_wait_list) > 0:
            request_id = charge_wait_list.pop(0)[0]
            charge_list.append(request_id)
            session.query(ChargeWaitArea).filter(
                ChargeWaitArea.request_id == request_id).delete()
        elif len(wait_list) > 0:
            request_id = wait_list.pop(0)[0]
            charge_list.append(request_id)
            session.query(WaitArea).filter(
                WaitArea.request_id == request_id).delete()
        else:  # 没有车了
            request_id = None

        # 写数据库:充电区队列、等候区队列，结束充电时间、即下一辆车开始充电时间;充电状态，新来的车充电信息
        session.query(ChargeRecord).filter(ChargeRecord.id == charge_done.id).update({
            "end_time": Timer().get_cur_format_time()
        })
        session.query(Charger).filter(Charger.id == charge_done.charge_pile_id).update({
            "cumulative_usage_times": session.query(Charger.cumulative_usage_times).filter(Charger.id == charge_done.charge_pile_id).first()[0] + 1,
            "cumulative_charging_time": session.query(Charger.cumulative_charging_time).filter(Charger.id == charge_done.charge_pile_id).first()[0]
            + charge_done.charge_time,
            "cumulative_charging_amount": str(float(session.query(Charger.cumulative_charging_amount).filter(Charger.id == charge_done.charge_pile_id).first()[0])
                                              + charge_done.require_amount)
        })
        session.query(ChargeRequest).filter(ChargeRequest.id == charge_done.id).update({
            "state": 0  # 不在充电
        })
        session.query(ChargeRequest).filter(ChargeRequest.id == request_id).update({
            "charge_pile_id": pile_id
        })
        if request_id is not None:
            session.add(ChargeArea(pile_id=pile_id, request_id=request_id))
            session.query(WaitArea).filter(
                WaitArea.request_id == request_id).delete()
            session.query(WaitQueue).filter(WaitQueue.charge_id == session.query(ChargeRequest.charge_id).filter(
                ChargeRequest.id == request_id).first()[0]).delete()
            session.query(ChargeWaitArea).filter(
                ChargeWaitArea.request_id == request_id).delete()
            if request_id == charge_list[0]:
                session.query(ChargeRequest).filter(ChargeRequest.id == request_id).update({
                    "state": 3  # 正在充电
                })
                session.query(ChargeRequest).filter(ChargeRequest.id == request_id).update({
                    "start_time": Timer().get_cur_timestamp()
                })
            else:
                session.query(ChargeRequest).filter(ChargeRequest.id == request_id).update({
                    "state": 2  # 充电区等待
                })

        first_req_id = charge_list[0] if len(charge_list) > 0 else None

        if first_req_id is not None:
            req = session.query(ChargeRequest).filter(
                ChargeRequest.id == first_req_id[0]).first()
            if req.state == 1 or req.state == 2 or req.state == 4 or req.state == 5:
                session.query(ChargeRequest).filter(ChargeRequest.id == first_req_id[0]).update({
                    "state": 3  # 正在充电
                })
                session.query(ChargeRequest).filter(ChargeRequest.id == first_req_id[0]).update({
                    "start_time": Timer().get_cur_timestamp()
                })

        session.commit()

    elif schedule_type is 2:  # 充电区队没满时，来了一辆车
        cur_state = session.query(ChargeRequest.state).filter(
            ChargeRequest.id == request_id).first()[0]
        if cur_state == 3 and not must_sch:
            return
        charge_mode = session.query(ChargeRequest.charge_mode).filter(
            ChargeRequest.id == request_id).first()[0]
        pile_id = session.query(ChargeRequest.charge_pile_id).filter(
            ChargeRequest.id == request_id).first()[0]
        charge_list = session.query(ChargeArea.request_id).filter(
            ChargeArea.pile_id == pile_id).all()
        charge_wait_list = session.query(ChargeWaitArea.request_id).filter(
            ChargeWaitArea.type == charge_mode).all()
        wait_list = session.query(WaitArea.request_id).filter(
            WaitArea.type == charge_mode).all()

        # 加入最快的队列-获取pile_id : 读队伍末尾车辆的结束时间
        endtime_list = []
        their_pile_id = []  # 与endtime_list的充电桩一一对应

        if charge_mode == "F":
            # 遍历每一个正常工作的快充桩
            for charger_tmp in session.query(Charger).filter(and_(Charger.type == "F", Charger.charger_status == "RUNNING")):
                now_queue_len = session.query(ChargeArea.request_id).filter(
                    ChargeArea.pile_id == charger_tmp.id).count()
                session.query(Charger).filter(Charger.id == charger_tmp.id).update({
                    "last_end_time": (session.query(Charger.last_end_time).filter(Charger.id == charger_tmp.id).first()[0] if now_queue_len != 0 else Timer().get_cur_timestamp())
                })
                now_queue_len = session.query(ChargeArea.request_id).filter(
                    ChargeArea.pile_id == charger_tmp.id).count()
                M = session.query(Charger.ChargingQueueLen).filter(
                    Charger.id == charger_tmp.id).first()[0]  # 充电桩排队队列长度
                if now_queue_len < M:  # 该充电区有空位
                    endtime_list.append(charger_tmp.last_end_time)
                    their_pile_id.append(charger_tmp.id)
        else:  # T-慢充
            for charger_tmp in session.query(Charger).filter(and_(Charger.type == "T", Charger.charger_status == "RUNNING")):
                now_queue_len = session.query(ChargeArea.request_id).filter(
                    ChargeArea.pile_id == charger_tmp.id).count()
                session.query(Charger).filter(Charger.id == charger_tmp.id).update({
                    "last_end_time": (session.query(Charger.last_end_time).filter(Charger.id == charger_tmp.id).first()[0] if now_queue_len != 0 else Timer().get_cur_timestamp())
                })
                now_queue_len = session.query(ChargeArea.request_id).filter(
                    ChargeArea.pile_id == charger_tmp.id).count()
                M = session.query(Charger.ChargingQueueLen).filter(
                    Charger.id == charger_tmp.id).first()[0]  # 充电桩排队队列长度
                if now_queue_len < M:  # 该充电区有空位
                    endtime_list.append(charger_tmp.last_end_time)
                    their_pile_id.append(charger_tmp.id)

        if endtime_list == []:
            if not error:
                return
            else:
                session.query(ChargeRequest).filter(ChargeRequest.id == request_id).update({
                    "state": 5
                })
                session.commit()
                return

        # 返回充电完成最快的充电桩编号
        pile_id = their_pile_id[endtime_list.index(min(endtime_list))]

        now_queue_len = session.query(ChargeArea.request_id).filter(
            ChargeArea.pile_id == pile_id).count()
        session.query(Charger).filter(Charger.id == pile_id).update({
            "last_end_time": (session.query(Charger.last_end_time).filter(Charger.id == pile_id).first()[0] if now_queue_len != 0 else Timer().get_cur_timestamp()) +
            session.query(ChargeRequest.charge_time).filter(
                ChargeRequest.id == request_id).first()[0]
        })
        if session.query(ChargeArea).filter(ChargeArea.request_id == request_id).count() == 0:
            session.add(ChargeArea(pile_id=pile_id, request_id=request_id))
        else:
            session.query(ChargeArea).filter(ChargeArea.request_id == request_id).update({
                "pile_id": pile_id
            })
        session.query(WaitArea).filter(
            WaitArea.request_id == request_id).delete()
        session.query(WaitQueue).filter(WaitQueue.charge_id == session.query(ChargeRequest.charge_id).filter(
            ChargeRequest.id == request_id).first()[0]).delete()
        session.query(ChargeWaitArea).filter(
            ChargeWaitArea.request_id == request_id).delete()

        charge_list = session.query(ChargeArea.request_id).filter(
            ChargeArea.pile_id == pile_id).all()
        # 直接到了队首，直接充电
        if str(request_id) == charge_list[0][0] and session.query(ChargeRequest).filter(
                and_(ChargeRequest.charge_pile_id == pile_id, ChargeRequest.state == 3)).first() is None:
            session.query(ChargeRequest).filter(ChargeRequest.id == request_id).update({
                "state": 3  # 正在充电
            })
            session.query(ChargeRequest).filter(ChargeRequest.id == request_id).update({
                "start_time": Timer().get_cur_timestamp()
            })
        else:
            session.query(ChargeRequest).filter(ChargeRequest.id == request_id).update({
                "state": 2 if not error else 5  # 充电区等待
            })
        # 写数据库
        session.query(ChargeRequest).filter(ChargeRequest.id == request_id).update({
            "charge_pile_id": pile_id
        })

        session.commit()

    elif schedule_type is 3:  # 充电桩开启
        charge_wait_list = session.query(ChargeWaitArea.request_id).filter(
            ChargeWaitArea.type == type).all()
        charge_wait_list = [i[0] for i in charge_wait_list]
        scheduling = True
        for charger_tmp in session.query(Charger).filter(and_(Charger.type == type, Charger.charger_status == "RUNNING")):
            now_queue_len = session.query(ChargeArea.request_id).filter(
                ChargeArea.pile_id == charger_tmp.id).count()
            if now_queue_len > 0:  # 有车辆排队
                tmp_list = session.query(ChargeArea.request_id).filter(
                    ChargeArea.pile_id == charger_tmp.id).all()
                charge_wait_list += [i[0] for i in tmp_list]  # 重新排队
        charge_wait_list.sort()
        # 后面应该接schedul(2)即可
        while(len(charge_wait_list) > 0):
            request_id = charge_wait_list[0]
            schedule(2, request_id)  # 里面会pop直至charge_wait_list调度完
            charge_wait_list.pop(0)
            scheduling = False
        session.commit()
        car_in_waitArea = session.query(WaitArea.request_id).filter(
            WaitArea.type == type).order_by(WaitArea.request_id).all()
        for request_id in car_in_waitArea:
            schedule(2, request_id[0])

    elif schedule_type is 4:  # 充电桩故障或关闭
        # 为当前充电的车辆记录时间戳
        charge_done = session.query(ChargeRequest).filter(
            and_(ChargeRequest.charge_pile_id == err_charger_id, ChargeRequest.state == 2)).all() + session.query(ChargeRequest).filter(
            and_(ChargeRequest.charge_pile_id == err_charger_id, ChargeRequest.state == 3)).all() + session.query(ChargeRequest).filter(
            and_(ChargeRequest.charge_pile_id == err_charger_id, ChargeRequest.state == 5)).all()
        if charge_done is None or len(charge_done) == 0:
            return

        for charge_done_tmp in charge_done:
            session.add(ChargeWaitArea(
                request_id=charge_done_tmp.id, type=charge_done_tmp.charge_mode))
            session.query(ChargeArea).filter(
                ChargeArea.request_id == charge_done_tmp.id).delete()

        session.commit()

        charge_wait_list = session.query(ChargeWaitArea.request_id).filter(
            ChargeWaitArea.type == charge_done[0].charge_mode).all()

        for request_id in charge_wait_list:
            schedule(2, request_id[0], must_sch=True, error=True)
        session.commit()
