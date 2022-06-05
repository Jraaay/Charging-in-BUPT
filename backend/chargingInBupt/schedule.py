from backend.chargingInBupt.orm import WaitArea
from chargingInBupt.orm import ChargeRecord, ChargeRequest, Charger, WaitArea
from requests import session
import os


def schedule(schedule_type,request_id):
    charge_mode = session.query(ChargeRequest.charge_mode).filter(ChargeRequest.id == request_id)
    
    if schedule_type is 1:  #有人完成充电 或者是取消充电
        charge_done = session.query(ChargeRequest).filter(ChargeRequest.id == request_id)
        pile_id = session.query(ChargeRequest.charge_pile_id).filter(ChargeRequest.id == request_id)
        charge_list = session.query(Charger.charge_list).filter(Charger.id == pile_id)
        charge_wait_list = session.query(WaitArea.charge_wait_list).filter(WaitArea.type == charge_mode)
        wait_list = session.query(WaitArea.wait_list).filter(WaitArea.type == charge_mode)
        #让该充电桩第二辆车充电
        charge_list.pop(0)
        #检查充电区的等候区、等候区，有则叫号进入充电区
        if len(charge_wait_list) > 0:
            request_id = charge_wait_list.pop(0)
            charge_list.append(request_id)
            session.query(WaitArea).filter(WaitArea.type == charge_mode).update({
                "charge_wait_list" : charge_wait_list
            })
        elif len(wait_list) > 0:
            request_id = wait_list.pop(0)
            charge_list.append(request_id)
            session.query(WaitArea).filter(WaitArea.type == charge_mode).update({
                "wait_list" : wait_list
            })
        else :  #没有车了
            request_id = None  
        
        #写数据库:充电区队列、等候区队列，结束充电时间、即下一辆车开始充电时间;充电状态，新来的车充电信息
        session.query(Charger).filter(Charger.id == pile_id).update({
            "charge_list" : charge_list
        })
        session.query(ChargeRecord).filter(ChargeRecord.id == charge_done.id).update({
            "end_time" : os.system('date +"%Y-%m-%d %H:%M:%S"')
        })
        session.query(ChargeRequest).filter(ChargeRequest.id == charge_done.id).update({
            "state" : 0  #不在充电
        })
        session.query(ChargeRequest).filter(ChargeRequest.id == request_id).update({
            "charge_id" : None,  #不再排队等候区
            "charge_pile_id" : pile_id
        })
        if request_id is not None :
            if request_id == charge_list[0]:
                session.query(ChargeRequest).filter(ChargeRequest.id == request_id).update({
                    "state" : 3  #正在充电
                })
                session.query(ChargeRecord).filter(ChargeRecord.id == request_id).update({
                    "start_time" : os.system('date +"%Y-%m-%d %H:%M:%S"')
                })
            else:
                session.query(ChargeRequest).filter(ChargeRequest.id == request_id).update({
                    "state" : 2  #充电区等待
            })
        

    elif schedule_type is 2:  #充电区队没满时，来了一辆车
        M = session.query(Charger.ChargingQueueLen)  #充电桩排队队列长度
        #加入最快的队列-获取pile_id : 读队伍末尾车辆的结束时间
        endtime_list = []
        their_pile_id = []  #与endtime_list的充电桩一一对应
        
        if charge_mode == "F" :
            #遍历每一个正常工作的快充桩
            for charger_tmp in session.query(Charger).filter(Charger.type=="F" and Charger.charger_status=="MAINTAINING"):
                if len(charger_tmp.charge_list) < M :  #该充电区有空位
                    endtime_list.append(charger_tmp.last_end_time)
                    their_pile_id.append(charger_tmp.id)
        else :  # T-慢充
            for charger_tmp in session.query(Charger).filter(Charger.type=="T" and Charger.charger_status=="MAINTAINING"):
                if len(charger_tmp.charge_list) < M :  #该充电区有空位
                    endtime_list.append(charger_tmp.last_end_time)
                    their_pile_id.append(charger_tmp.id)
        
        #返回充电完成最快的充电桩编号
        pile_id = their_pile_id[endtime_list.index(min(endtime_list))]
        charge_list = session.query(Charger.charge_list).filter(Charger.id == pile_id)
        charge_list.append(request_id)  #加入该最快队列
        
        #写数据库
        session.query(ChargeRequest).filter(ChargeRequest.id == request_id).update({
            "charge_id" : None,  #不再排队等候区
            "charge_pile_id" : pile_id
        })
        session.qurey(Charger).filter(Charger.id == pile_id).update({
            "charge_list" : charge_list ,
            "last_end_time" : session.query(Charger.last_end_time).filter(Charger.id==pile_id) + \
                session.query(ChargeRequest.charge_time).filter(ChargeRequest.id==request_id)
        })
        if request_id == charge_list[0]:  #直接到了队首，直接充电
            session.query(ChargeRequest).filter(ChargeRequest.id == request_id).update({
                "state" : 3  #正在充电
            })
            session.query(ChargeRecord).filter(ChargeRecord.id == request_id).update({
                "start_time" : os.system('date +"%Y-%m-%d %H:%M:%S"')
            })
        else :
            session.query(ChargeRequest).filter(ChargeRequest.id == request_id).update({
                "state" : 2  #充电区等待
            })        
        