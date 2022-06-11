from chargingInBupt.port import app
from chargingInBupt.Timer import Timer
from chargingInBupt.orm import Charger, session
from chargingInBupt.finishChecker import check_finish

if __name__ == "__main__":
    timer = Timer()
    session.commit()
    app.add_task(check_finish)
    app.run(debug=False)
