from selenium import webdriver
import time
import logging
from sqlalchemy import create_engine
import pandas as pd
import numpy as np
import pymysql.cursors

# 创建一个logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)  # Log等级总开关

# 创建一个handler,用于写入日志文件
logfile = './log.txt'
fh = logging.FileHandler(logfile, mode='a')

# 创建一个handler,用于输出到控制台
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)  # 输出到console的log等级开关

formatter = logging.Formatter("%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s")
fh.setFormatter(formatter)
ch.setFormatter(formatter)

# 第五步，将logger添加到handler里面
logger.addHandler(fh)
logger.addHandler(ch)


def get_data(driver, url, current_page, href, park_df, proviceName, totalPage, spellHref):
    """

    :param totalPage: 总页码
    :param spellHref:
    :param park_df: 爬取得到的数据存放
    :param proviceName: 爬取的省份名称
    :param driver: url驱动
    :param url: 爬取的网页url
    :param current_page:当前爬取的页面
    :param href:
    """
    logger.info('现在的页码：' + str(current_page))
    if url != '':
        driver.get(url)
    time.sleep(10)

    if href == '':
        try:
            href = driver.find_element_by_link_text('末页').get_attribute('href')
            href_arr = href.split('&page=')
            spell_href = href_arr[0]
            total_page = href_arr[1]
        except Exception as e:
            total_page = 1

    elements = driver.find_elements_by_class_name('fact_list')
    for ele in elements:
        time.sleep(10)
        park = {}
        park_name = ''
        address = ''
        level = ''

        park_name = ele.find_element_by_class_name('fact_tit').find_element_by_tag_name('a').text

        # 查找符合条件的第几个 find_elements_by...[i](第一个的下标是0)
        level = ele.find_element_by_class_name('fact_tit').find_elements_by_tag_name('span')[1].text
        address = ele.find_element_by_class_name('fact_date').text
        park_address = ele.find_element_by_class_name('fact_add').text
        area = ele.find_element_by_class_name('fact_area').text
        logger.info('park_name %s;address:%s', park_name, address)
        city_name = ''
        try:
            city_name = park_address[0:3]
        except Exception as e:
            print('查找城市名字报错:'+e)

        set_key = city_name + '_' + park_name
        if not judge_park(set_key):

            #driver.close()

            park_info_href = ele.find_element_by_class_name('fact_tit').find_element_by_tag_name('a').get_attribute('href')


            #打开园区详情页
            #通过js打开新页面
            js = 'window.open(\'' + park_info_href + '\')'
            #print(js)
            driver.execute_script(js)#打开新窗口

            time.sleep(10)

            # 实现页面的切换
            it = driver.window_handles

            driver.switch_to.window(it[1])  # 切换到新打开的窗口
            ele_all = driver.find_elements_by_class_name('informationli')

            # type(ele_all)
            # print(len(ele_all))

            mainIndustry = ''  # 主导产业
            infrastructure = ''  # 基础设施
            infrastructureInfo = ''  # 基础设施详细信息
            parkArea = ''  # 园区面积
            landPrice = ''  # 土地价格
            invest = ''  # 投资强度
            revenue = ''  # 税收要求
            carrieroperator = ''  # 运营商
            totalArea = ''
            alreadyArea = ''

            for i in range(0, len(ele_all)):
                content = ele_all[i].find_element_by_class_name('inf_right').text.replace('\n', '-')
                # print(content)
                if i == 0:
                    mainIndustry = content
                elif i == 1:
                    totalArea = content.split('平方公里')[0]
                    alreadyArea = content.split('平方公里')[1].split('已开发')[1]
                elif i == 2:
                    landPrice = content.split('万')[0]
                    print(landPrice)
                elif i == 3:
                    invest = content.split('万')[0]
                elif i == 4:
                    revenue = content.split('万')[0]
                elif i == 6:
                    carrieroperator = content

            infrastructure = driver.find_element_by_class_name('informationli2').find_element_by_class_name(
                'inf_right2').find_element_by_xpath('.//em').text

            infrastructureInfo = driver.find_element_by_class_name('informationli2').find_element_by_class_name(
                'inf_right2').text.replace('\n', '-')

            #print(infrastructure)
            #print(infrastructureInfo)
            driver.find_element_by_link_text('园区详情').click()
            infoContent = ''
            eles = driver.find_elements_by_id('info_body')
            for ele in eles:
                infoContent = infoContent + (ele.text)
            print(infoContent)

            park_dict = {}
            park_dict['park_name'] = park_name
            park_dict['address'] = address
            park_dict['city_name']=city_name
            park_dict['total_area'] = totalArea
            park_dict['already_area'] = alreadyArea
            park_dict['park_level'] = level
            #park_dict['park_link'] = park_link

            #park_df = pd.DataFrame()
            park_df = park_df.append(park_dict, ignore_index=True)
            driver.close()
            driver.switch_to.window(it[0])
            #print('*********')
            #print(park_df)
            #save_data(park_df)

    current_page += 1
    total_page = '1'
    if int(total_page) >= current_page:
        next_href = spell_href + '&page=' + str(current_page)
        #通过js打开新页面
        js = 'window.open(\'' + next_href + '\')'
        #print(js)
        driver.execute_script(js)#打开新窗口

        it = driver.window_handles

        driver.switch_to.window(it[0])  # 这是前一个页面it[1]是新打开的页面
        driver.close()  # 关闭上一个页面
        driver.switch_to.window(it[1])  # 切换到新打开的窗口
        time.sleep(5)
        get_data(driver,'', current_page, href, park_df, proviceName, total_page, spell_href)

    else:
        save_data(park_df)
        logger.info('保存数据，一个省份完成' + proviceName)
        return

# def save_data():
#     import pymysql.cursors
#     connection = pymysql.connect(host='localhost', port=3306, user='root', passwd='123456', db='it_fica',
#                                  charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
#     sql = ''
#     try:
#         cursors = connection.cursor()
#         cursors.execute(sql)
#     except Exception:
#         logger.error('查询失败')
#     cursors.close()

def save_data(park_df):
    # 初始化数据库连接，使用pymysql模块
    engine = create_engine('mysql+pymysql://root:123456@localhost:3306/mytest')
    # df = pd.DataFrame({'id': [1, 2, 3], 'name': ['zhangsan', 'lisi', 'wangermazi']})
    #df = pd.DataFrame({'name': ['zhangsan', 'lisi', 'wangermazi']})
    park_df.to_sql('t_park_info', engine, if_exists='append', index=False)



def judge_park(setkey):
    # 初始化数据库连接，使用pymysql模块
    engine = create_engine('mysql+pymysql://root:123456@localhost:3306/mytest')
    sql = 'select city_name,park_name from t_park_info'
    data = pd.read_sql(sql,engine)
    #print(data)
    #print(type(data))
    if len(data)>1:
        keys = data['city_name']+'_'+data['park_name']
        #print(keys)
        if setkey in keys.values:
            return True
        else:return False
    else:return False



if __name__ == '__main__':
    #print(judge_park('河北_河北工业区'))
    driver: webdriver = webdriver.Chrome()
    url = 'http://hb.cnipai.com/park/'
    park_list = pd.DataFrame()
    get_data(driver, url, 1, '', park_list, 'hebei', '', '')

