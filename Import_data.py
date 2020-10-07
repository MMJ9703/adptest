#%%----------------------------------------------------------------------------
import pandas
import numpy as np
import requests
import time,datetime

def timestamp(x):
    timeArray = time.strptime(str(x), '%Y-%m-%d %H:%M:%S')
    timeStamp = int(time.mktime(timeArray))
    return timeStamp * 1000

class Data_Collection():
    def __init__(self):
        self.Token = Data_Collection.get_token()
    @staticmethod
    def get_token():
        user_name = 'U0JXdG9ETFVU'
        pass_word = 'MjU4MDA1MDM'
        url = 'http://data.shenguyun.com:8088/sgck-datainterface/v1/login?' \
              'name=' + user_name + '&pwd=' + pass_word + '='
        response = requests.get(url)
        if response.content:
            token = response.json()['token']
            return token
    #获取单台机组信息
    def single_unit(self, ID):
        ID = ID
        url = 'http://data.shenguyun.com:8088/sgck-datainterface/v1/positions?'\
                  'token='+self.Token+'&macids='+str(ID)
        response = requests.get(url)
        if response.content:
            all_data = response.json()['data']
            for i in range(0,len(all_data)):
                print('机组：',all_data[i]['macid'],all_data[i]['macName'])
                positons = all_data[i]['positons']
                id = [];unit = [];itemNo = [];name = [];type = []
                for j in range(0,len(positons)):
                    id.append(str(positons[j]['id']))
                    try:
                        unit.append(positons[j]['unit'])
                    except KeyError:
                        unit.append('')
                    itemNo.append(positons[j]['itemNo'])
                    name.append(positons[j]['name'])
                    type.append(positons[j]['type'])

                
                final_data = pandas.DataFrame({'id':id,'unit':unit,'itemNo':itemNo,'name':name,'type':type})
                return final_data
    #获取机组历史数据
    def history_data(self, ID, Input_Time, days):
        ID = ID
        Input_Time = Input_Time
        days = int(days)

        
        data_file = self.single_unit(ID)
        
        G = []
        for k, group in data_file.groupby(['type']):
            G.append([k,group])
        data_list = []
        data_type = []
        for g in G:
            type = g[0]
            Data = g[1]
            ID_ = Data['id'].tolist()
            NAME = Data['name'].tolist()
            TYPE = Data['type'].tolist()

            dataframe_merge = []
            end_datetime = datetime.datetime.strptime(Input_Time, '%Y-%m-%d %H:%M:%S')
            for time_stemp in range(1,days+1):
                end_timeStamp = timestamp(end_datetime)
                start_timeStamp = timestamp(end_datetime - datetime.timedelta(days=1))
                print('%s次:' % time_stemp)
                name_row = 0
                index_time = []
                final_dataframe = []
                for positions_id in ID_:
                    print(name_row, '测点：', positions_id, NAME[name_row],'Type:',TYPE[name_row])
                    url = 'http://data.shenguyun.com:8088/sgck-datainterface/v1/hisdata?' \
                              'token=' + self.Token + '&posid=' + str(positions_id) + \
                              '&codes=' + '&start=' + str(start_timeStamp) + '&end=' + str(end_timeStamp)
                    response = requests.get(url)
                    #1.如果测点为振动量
                    if type == 'PT_VIB':
                        DataTime = [];Value = [];TimeStemp1 = []
                        Gap = [];Rms = []
                        Pp_value = [];P_value = []
                        Half_freq = [];One_freq_x = [];One_freq_y = []
                        Two_freq_x = [];Two_freq_y = [];Speed = [];Remain_freq = []
                        if response.content:
                            all_data_vib = response.json()['data']
                        for i in range(0, len(all_data_vib)):
                            timestemp_ = all_data_vib[i]['datatime']
                            TimeStemp1.append(timestemp_)
                            time_local = time.localtime(int(timestemp_) / 1000)
                            datatime = time.strftime("%Y-%m-%d %H:%M:%S", time_local)
                            DataTime.append(datatime)
                            Gap.append(all_data_vib[i]['gap'])
                            Rms.append(all_data_vib[i]['rms'])
                            Pp_value.append(all_data_vib[i]['pp_value'])
                            P_value.append(all_data_vib[i]['p_value'])
                            Half_freq.append(all_data_vib[i]['half_freq'])
                            One_freq_x.append(all_data_vib[i]['one_freq_x'])
                            One_freq_y.append(all_data_vib[i]['one_freq_y'])
                            Two_freq_x.append(all_data_vib[i]['two_freq_x'])
                            Two_freq_y.append(all_data_vib[i]['two_freq_y'])
                            Speed.append(all_data_vib[i]['speed'])
                            Remain_freq.append(all_data_vib[i]['remain_freq'])
                        Value.append(Gap)
                        Value.append(Rms)
                        Value.append(Pp_value)
                        Value.append(P_value)
                        Value.append(Half_freq)
                        Value.append(One_freq_x)
                        Value.append(One_freq_y)
                        Value.append(Two_freq_x)
                        Value.append(Two_freq_y)
                        Value.append(Speed)
                        Value.append(Remain_freq)
                        Value = np.swapaxes(np.array(Value), 0, 1)

                        index_time.append(DataTime)
                        F = pandas.DataFrame(Value,columns = [[NAME[name_row]]*11,
                                                                                  ['gap','rms','pp_value','p_value',
                                                                                  'half_freq','one_freq_x','one_freq_y','two_freq_x',
                                                                                  'two_freq_y','speed','remain_freq']])
                        F['时间戳'] = TimeStemp1
                        final_dataframe.append(F)
                        name_row = name_row + 1
                    #2.如果测点为转速量
                    if type == 'PT_SPEED':
                        DataTime = [];TimeStemp2 = [];Speed = [];Gap = [];Value = []
                        if response.content:
                            all_data_speed = response.json()['data']
                        for i in range(0, len(all_data_speed)):
                            timestemp_ = all_data_speed[i]['datatime']
                            TimeStemp2.append(timestemp_)
                            time_local = time.localtime(int(timestemp_) / 1000)
                            datatime = time.strftime("%Y-%m-%d %H:%M:%S", time_local)
                            DataTime.append(datatime)
                            Speed.append(all_data_speed[i]['speed'])
                            Gap.append(all_data_speed[i]['gap'])
                        Value.append(Speed)
                        Value.append(Gap)
                        Value = np.swapaxes(np.array(Value),0,1)

                        index_time.append(DataTime)
                        F = pandas.DataFrame(Value,columns = [[NAME[name_row],NAME[name_row]],['speed','gap']])
                        F['时间戳'] = TimeStemp2
                        final_dataframe.append(F)
                        name_row = name_row + 1

                    #3.如果测点为过程量
                    if type == 'PT_STATIC':
                        DataTime = [];TimeStemp3 = [];Value = []
                        if response .content:
                            all_data_static = response.json()['data']
                        for i in range(0, len(all_data_static)):
                            timestemp_ = all_data_static[i]['datatime']
                            TimeStemp3.append(timestemp_)
                            time_local = time.localtime(int(timestemp_) / 1000)
                            datatime = time.strftime("%Y-%m-%d %H:%M:%S", time_local)
                            DataTime.append(datatime)
                            try:
                                Value.append(all_data_static[i]['value'])
                            except KeyError:
                                Value.append('')
                        index_time.append(DataTime)
                        F = pandas.DataFrame({NAME[name_row]: Value})
                        F['时间戳'] = TimeStemp3
                        final_dataframe.append(F)
                        name_row = name_row + 1

                result = pandas.concat(final_dataframe, axis=1)
                #横向合并dataframe
                cols = list(result.columns)
                for i, item in enumerate(result.columns):
                    if item in result.columns[:i]:
                        cols[i] = "toDROP"
                result.columns = cols
                if "toDROP" in result.columns:
                    result = result.drop("toDROP", 1)
                #删除dataframe合并后的重复列
                result['Time']=sorted(index_time,key = lambda i:len(i),reverse=True)[0]
                result = result.set_index('Time')
                #添加时间索引
                dataframe_merge.append(result)#纵向合并dataframe
                end_datetime = end_datetime - datetime.timedelta(days=1)
            
            final_data = pandas.concat(dataframe_merge).sort_index()
            fianl_data = final_data.reset_index()
            data_list.append(final_data)
            data_type.append(type)
        return data_list, data_type
#%%----------------------------------------------------------------------------
import pandas as pd
import pymysql
from sqlalchemy import create_engine
def mainf(ID, Input_Time, days, engine):
    d_lst, d_type = Data_Collection().history_data(ID, Input_Time, days)
    for i in range(len(d_lst)):
        df = d_lst[i].reset_index()
        # engine = create_engine("mysql+pymysql://root:123456@localhost:3306/test")
        df.to_sql(name = 'id'+str(ID)+d_type[i].lower(),con = engine,if_exists = 'replace',index = False,index_label = False)
    status = 'finish'
    print(status)
    return status
