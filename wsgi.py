# -*- coding: utf8 -*-
# 添加所需要的库
import os
# 添加自己编写的算法
from Import_data import mainf
from read_information import *
from DWPB_denoising import DWPB
# Web应用程序设置
from flask_executor import Executor
from flask import request
import pandas as pd
from threading import Thread

from sqlalchemy import create_engine


from flask import Flask
from flask import request
from flask_cors import *

application = Flask(__name__)
executor = Executor(application)
# 获取mysql环境变量
# os.environ['MYSQL_URI'] = 'mysql+pymysql://root:123456@localhost:3306/test'
env = os.environ
# MYSQL_URI   mysql+pymysql://test:test@172.30.238.185:3306/test
mysql_uri = env.get('MYSQL_URI')

sqlEngine = create_engine(mysql_uri, pool_recycle=3600)

print ('=== mysql uri: ' + mysql_uri)

def import_data_task(data):  
    try:

        print ('===== run task')
        # 机组信息
        # ID = 150817080435211
        # Input_Time = '2020-6-20 00:00:00'
        # days = 1
        ID,Input_Time,days = read_json(data)
        # 算法执行
        status = mainf(ID, Input_Time, days, sqlEngine)
        # data["param"]["status"] = status
    except Exception as e:
        print ('===error===')
        print (e)
        # data["param"]["status"] = 'error'
        raise e
    return True
def algorithm_task(data):
    try:

        print ('===== run task')
        # 机组信息
        # ID = 150817080435211
        # tpye = 'vib'
        ID = data["param"]["id"]
        tpye = data["param"]["type"]
        table_name_1 = 'id'+str(ID)+'pt_'+tpye
        data_1 = pd.read_sql("select * from  "+table_name_1 , con=sqlEngine, index_col=None)

        data_1['Time'] = pd.to_datetime(data_1['Time'],format='%Y-%m-%d %H:%M:%S')
        data_1 = data_1.set_index('Time')
        data_1 = data_1.dropna()
        clean_data= DWPB('db8',3).denoising_process(data_1)

        # 将数据写入mysql数据库中，设置查询pd.to_sql()函数
        table_name_2 =  'clean_data_'+'id'+str(ID)+'pt_'+tpye
        data_1.to_sql(table_name_2, con=sqlEngine, if_exists='replace', index=True)
        print ('finish')

    except Exception as e:
        print ('===error===')
        print (e)
        raise e
    return True

# rest  api（应用执行端口）
@application.route('/')
def hello():
    return "OK"
# @application.route('/unitdata', methods=['POST'])
# def unitdata():
#     data = request.get_json()
#     executor.submit(import_data_task,data)
#     return "loading"
# @application.route('/algorithm', methods=['POST'])
# def algorithm():
#     data = request.get_json()
#     executor.submit(algorithm_task,data)
#     return "loading"
if __name__ == '__main__':

    application.run(port=8080)

