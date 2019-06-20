
from pyparrot.Bebop import Bebop
import keyboard

bebop = Bebop()

while True :
    try:
        if keyboard.is_pressed ('e'):
            print("The killswicht was activated.")
            bebop.smart_sleep(5)
            bebop.safe_land(10)

            bebop.smart_sleep(5)
            bebop.disconnect()
        else:
            pass
    except:
        break