from kivy_final_v3 import start_ui
#from kivy_main_v3 import update_img
from final_server_v2 import fr_check 
from final_server_v2 import rfid_check

import multiprocessing

def main():
    print("main start")
    q = multiprocessing.Queue(maxsize = 10)  #####queue maximum size
    print("queue size : ", q.qsize())
    fr = multiprocessing.Process(target= fr_check, args=(q,))
    rfid = multiprocessing.Process(target=rfid_check, args=(q,))
    ui_start = multiprocessing.Process(target = start_ui, args=(q,))
    fr.start()
    rfid.start()
    ui_start.start()
    print("main end")


if __name__ == "__main__":
    main()