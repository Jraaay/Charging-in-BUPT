from tkinter.tix import Tree
from sympy import true
from backend.chargingInBupt.orm import WaitArea
from chargingInBupt.orm import ChargeRecord, ChargeRequest, Charger, ChargeArea, ChargeWaitArea, WaitArea
from requests import session
import Timer


def schedule(schedule_type,request_id):
    charge_mode = session.query(ChargeRequest.charge_mode).filter(ChargeRequest.id == request_id)
    pile_id = session.query(ChargeRequest.charge_pile_id).filter(ChargeRequest.id == request_id)
    charge_list = session.query(ChargeArea.request_id).filter(ChargeArea.pile_id == pile_id)
    charge_wait_list = session.query(ChargeWaitArea.request_id).filter(ChargeWaitArea.type == charge_mode)
    wait_list = session.query(WaitArea.request_id).filter(WaitArea.type == charge_mode)
     
    if schedule_type is 1:  #有人完成充电 或者是取消充电
        charge_done = session.query(ChargeRequest).filter(ChargeRequest.id == request_id)
        
        #让该充电桩第二辆车充电
        charge_list.pop(0)
        #检查充电区的等候区、等候区，有则叫号进入充电区
        if len(charge_wait_list) > 0:
            request_id = charge_wait_list.pop(0)
            charge_list.append(request_id)
            session.query(ChargeWaitArea).filter(ChargeWaitArea.request_id == request_id).delete()
        elif len(wait_list) > 0:
            request_id = wait_list.pop(0)
            charge_list.append(request_id)
            session.query(WaitArea).filter(WaitArea.request_id == request_id).delete()
        else :  #没有车了
            request_id = None  
        
        timer = Timer()
        #写数据库:充电区队列、等候区队列，结束充电时间、即下一辆车开始充电时间;充电状态，新来的车充电信息
        session.query(ChargeRecord).filter(ChargeRecord.id == charge_done.id).update({
            "end_time" : timer.get_cur_format_time()
        })
        session.query(Charger).filter(Charger.id == charge_done.charge_pile_id).update({
            "cumulative_usage_times" : session.query(Charger.cumulative_usage_times).filter(Charger.id == charge_done.charge_pile_id) + 1 ,
            "cumulative_charging_time" : session.query(Charger.cumulative_charging_time).filter(Charger.id == charge_done.charge_pile_id) \
                + charge_done.charge_time ,
            "cumulative_charging_amount" : str(float(session.query(Charger.cumulative_charging_amount).filter(Charger.id == charge_done.charge_pile_id)) \
                + charge_done.require_amount )
        })
        session.query(ChargeRequest).filter(ChargeRequest.id == charge_done.id).update({
            "state" : 0  #不在充电
        })
        session.query(ChargeRequest).filter(ChargeRequest.id == request_id).update({
            "charge_id" : None,  #不再排队等候区
            "charge_pile_id" : pile_id
        })
        if request_id is not None :
            session.add(ChargeArea(pile_id=pile_id,request_id=request_id))
            if request_id == charge_list[0]:
                session.query(ChargeRequest).filter(ChargeRequest.id == request_id).update({
                    "state" : 3  #正在充电
                })
                session.query(ChargeRequest).filter(ChargeRequest.id == request_id).update({
                    "start_time" : timer.get_cur_format_time()
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
                now_queue_len = session.query(ChargeArea.request_id).filter(ChargeArea.pile_id == charger_tmp.pile_id).count()
                if now_queue_len < M :  #该充电区有空位
                    endtime_list.append(charger_tmp.last_end_time)
                    their_pile_id.append(charger_tmp.id)
        else :  # T-慢充
            for charger_tmp in session.query(Charger).filter(Charger.type=="T" and Charger.charger_status=="MAINTAINING"):
                now_queue_len = session.query(ChargeArea.request_id).filter(ChargeArea.pile_id == charger_tmp.pile_id).count()
                if now_queue_len < M :  #该充电区有空位
                    endtime_list.append(charger_tmp.last_end_time)
                    their_pile_id.append(charger_tmp.id)
        
        #返回充电完成最快的充电桩编号
        pile_id = their_pile_id[endtime_list.index(min(endtime_list))]
        
        timer = Timer()
        #写数据库
        session.add(ChargeArea(pile_id=pile_id,request_id=request_id))
        session.query(ChargeRequest).filter(ChargeRequest.id == request_id).update({
            "charge_id" : None,  #不再排队等候区
            "charge_pile_id" : pile_id
        })
        session.qurey(Charger).filter(Charger.id == pile_id).update({
            "last_end_time" : session.query(Charger.last_end_time).filter(Charger.id==pile_id) + \
                session.query(ChargeRequest.charge_time).filter(ChargeRequest.id==request_id)
        })
        
        charge_list = session.query(ChargeArea.request_id).filter(ChargeArea.pile_id == pile_id)
        if request_id == charge_list[0]:  #直接到了队首，直接充电
            session.query(ChargeRequest).filter(ChargeRequest.id == request_id).update({
                "state" : 3  #正在充电
            })
            session.query(ChargeRequest).filter(ChargeRequest.id == request_id).update({
                "start_time" : timer.get_cur_format_time()
            })
        else :
            session.query(ChargeRequest).filter(ChargeRequest.id == request_id).update({
                "state" : 2  #充电区等待
            })        
        

    elif schedule_type is 3:#充电桩开启
        scheduling = True
        for charger_tmp in session.query(Charger).filter(Charger.type == type and Charger.charger_status=="MAINTAINING"):
                now_queue_len = session.query(ChargeArea.request_id).filter(ChargeArea.pile_id == charger_tmp.pile_id).count()
                if now_queue_len > 0 : #有车辆排队
                    tmp_list = session.query(ChargeArea.request_id).filter(ChargeArea.pile_id == charger_tmp.pile_id)
                    charge_wait_list.append(tmp_list)#重新排队
        charge_wait_list.sort()
        #后面应该接schedul(2)即可
        while(len(charge_wait_list)>0):
            for charger_tmp in session.query(Charger).filter(Charger.type==type and Charger.charger_status=="MAINTAINING"):
                if(len(charger_tmp.chargelist) < M):
                    request_id = charge_wait_list[0]
                    schedule(2,request_id)#里面会pop直至charge_wait_list调度完
            scheduling = False
            
          

                    

    elif schedule_type is 4:#充电桩故障或关闭
        #为当前充电的车辆记录时间戳
        charge_done = session.query(ChargeRequest).filter(ChargeRequest.id == request_id)
        timer = Timer()
        session.query(ChargeRecord).filter(ChargeRecord.id == charge_done.id).update({
            "end_time" : timer.get_cur_format_time()
        })
        session.query(Charger).filter(Charger.id == charge_done.charge_pile_id).update({
            "cumulative_usage_times" : session.query(Charger.cumulative_usage_times).filter(Charger.id == charge_done.charge_pile_id) + 1 ,
            "cumulative_charging_time" : session.query(Charger.cumulative_charging_time).filter(Charger.id == charge_done.charge_pile_id) \
                + charge_done.charge_time ,
            "cumulative_charging_amount" : str(float(session.query(Charger.cumulative_charging_amount).filter(Charger.id == charge_done.charge_pile_id)) \
                + charge_done.require_amount )
        })
        session.query(ChargeRequest).filter(ChargeRequest.id == charge_done.id).update({
            "state" : 0  #不在充电
        })

        #进行调度
        for charger_tmp in session.query(Charger).filter(Charger.type == type  and Charger.charger_status=="MAINTAINING"):
                now_queue_len = session.query(ChargeArea.request_id).filter(ChargeArea.pile_id == charger_tmp.pile_id).count()
                if now_queue_len < M :  #同类型充电桩有空位
                    charge_wait_list.append(charge_list)#优先调度
                    break
        charge_list.clear()
        charge_wait_list.sort()#时间调度
        #更新等待队列
        session.query(ChargeArea).filter(ChargeArea.pile_id == pile_id).update({
            "request_id" : charge_list
            })
        session.qurey(ChargeWaitArea).filterfilter(ChargeWaitArea.type == charge_mode).update({
            "ChargeWaitArea.request_id" : charge_wait_list
            })

        while(len(charge_wait_list)>0):
            for charger_tmp in session.query(Charger).filter(Charger.type==type and Charger.charger_status=="MAINTAINING"):
                if(len(charger_tmp.chargelist) < M):
                    request_id = charge_wait_list[0]
                    schedule(2,request_id)#里面会pop直至charge_wait_list调度完
                

                

