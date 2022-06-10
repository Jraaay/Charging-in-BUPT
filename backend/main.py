from chargingInBupt.port import app
from chargingInBupt.Timer import Timer
from chargingInBupt.orm import Charger, session

if __name__ == "__main__":
    timer = Timer()
    chargers = session.query(Charger).all()
    for charger in chargers:
        charger.cumulative_usage_times = 0
        charger.cumulative_charging_time = 0
        charger.cumulative_charging_amount = "0"
        charger.start_time = timer.get_cur_timestamp()
    session.commit()
    app.run()
