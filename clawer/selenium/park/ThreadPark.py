# -*- coding: UTF-8 -*-
import threading
import time
from selenium import webdriver
import pandas as pd

import ParkUtil
from ParkService import get_data

exitFlag = 0
web_driver_map = {}

def do_task():
    # 创建新线程

    for key in ParkUtil.pnameMap.keys():
        thread1 = myThread(key, ParkUtil.pnameMap.get(key))
        # 开启线程
        thread1.start()

        for key in web_driver_map.keys():
            print('key' + '----close')
            web_driver_map[key].close()

        for key in web_driver_map.keys():
            print('key' + '----quit')
            web_driver_map[key].quit()

class myThread(threading.Thread):  # 继承父类threading.Thread
    def __init__(self, province_url, province_name):
        threading.Thread.__init__(self)
        self.province_url = province_url
        self.province_name = province_name

    def run(self):
        try:
            park_list = pd.DataFrame()
            print('aaaa')
            thread_name = threading.Thread.getName(self)
            print("starting" + self.province_name + " threadname:" + thread_name)
            web_driver_map[thread_name] = get_web_driver()
            get_data(web_driver_map.get(thread_name), self.province_url, 1, '', park_list, self.province_name, 1, '')
            print("Exiting " + self.province_name + " threadname:" + thread_name)
        except Exception as e:
            print('报错:'+e)




def get_web_driver():
    driver: webdriver = webdriver.Chrome()
    return driver

if __name__ == '__main__':
    do_task()
