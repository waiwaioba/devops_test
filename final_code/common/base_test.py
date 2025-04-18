# 存储公共的函数
# 断言的封装函数
import json
import jsonpath
import openpyxl
from requests import request
from loguru import logger
from string import Template
from common.db_util import query_data

# 类似于postman环境变量-存储接口之间传递的数据用的
env_dict = {}

# 去执行用例数据的统一函数
def execute_case(case_data):
    # 1、执行请求
    res = send_request(case_data)
    # 2、提取响应字段
    extract_res(res ,case_data)
    # 3、接口响应断言
    assert_res(case_data,res)
    # 4、数据库断言
    assert_db(case_data)

# 提取响应的封装的函数
def extract_res(res,case_data):
    extract_data = case_data.get('提取响应字段')
    extract_dict = json_convert_dict(extract_data)
    if extract_dict:
        # for循环遍历字典  {"token":"$..access_token"}
        for k, v in extract_dict.items():
            # 两种情况：1、提取响应体文本  2、提取响应字段的值
            if v == 'text':
                env_dict[k] = res.text
            else:
                # 通过jsonpath表达式获取实际响应字段的值
                value = jsonpath.jsonpath(res.json(), v)[0]
                # 把获取到的数据保存到环境变量中，键值对：键->变量名  值：获取的实际字段的值
                env_dict[k] = value

# 读取excel通用的封装，后续自动化可以直接复用
def read_excel(file_path, sheet_name):
    """
    读取Excel文件的封装函数
    :param file_path: excel文件的路径
    :param sheet_name: 读取的sheet名称
    :return: 列表嵌套字典的数据结构
    """
    wb = openpyxl.load_workbook(file_path)
    sh = wb[sheet_name]
    li = []
    data_li = list(sh.values)
    header = data_li[0]
    for value in data_li[1:]:
        dict_data = dict(zip(header, value))
        li.append(dict_data)
    return li

# 封装标记替换的函数
def replace_by_mark(data):
    if data is not None:
        return Template(data).substitute(env_dict)

# json数据转换为字典的封装函数（判空的处理）
def json_convert_dict(data):
    if data is not None:
        return json.loads(data)

# 封装一个统一处理接口请求的函数
def send_request(case_data):
    # case_data 里面保存的就是每一条用例数据（包括接口请求四大要素-请求方法、请求地址、请求头、请求参数）
    method = case_data['请求方法']
    url = replace_by_mark(case_data['请求地址'])
    header = replace_by_mark(case_data['请求头'])
    params = replace_by_mark(case_data['请求参数'])
    logger.info('===========================接口请求日志========================')
    logger.info(f'请求方法:{method}')
    logger.info(f'接口地址:{url}')
    logger.info(f'请求头:{header}')
    logger.info(f'请求参数:{params}')

    # 通过requests库的request函数实际发送接口请求
    # 传递请求头（headers关键字）、请求参数（json、data、params..）的时候都必须要使用字典
    res = None
    header_dict = json_convert_dict(header)
    # 核心逻辑判断- 判断不同的请求方法、不同的传参类型
    if method.lower()  == 'get':
        res = request(method,url,headers=header_dict,params=json_convert_dict(params))
    elif method.lower() == 'post' or method.lower() == 'put':
        type = header_dict['Content-Type']
        # 1、json传参
        if 'application/json' in type:
            res = request(method,url,headers=header_dict,json=json_convert_dict(params))
        # 2、form表单传参
        elif 'application/x-www-form-urlencoded' in type:
            res = request(method,url,headers=header_dict,data=json_convert_dict(params))
        # 3、文件上传
        elif 'multipart/form-data' in type:
            # request要求，在进行文件上传的时候不能传递multipart/form-data请求头，需要去掉
            header_dict.pop('Content-Type')
            res = request(method,url,headers=header_dict,files=eval(params))
    elif method.lower() == 'delete':
        print('这里补充delete请求方法的逻辑')
    logger.info('===========================接口响应日志========================')
    logger.info(f'响应状态码:{res.status_code}')
    logger.info(f'响应头:{res.headers}')
    logger.info(f'响应体:{res.text}')
    logger.info(f'响应时间:{res.elapsed.total_seconds()}秒')
    return res

# 封装一个统一处理接口响应断言的函数
def assert_res(case_data, res):
    """
    统一的断言封装
    :param case_data: 从excel中读取到每一行测试用例数据
    :param res: 接口的实际响应结果
    :return:
    """
    # 断言设计，断言统一封装处理
    expected = case_data['期望结果']
    logger.info('===========================响应断言日志========================')
    # 转换获取到字典类型的数据
    expected_dict = json_convert_dict(expected)
    if expected_dict:
        # 拿到字典中所有的信息（for循环？？）
        for k, v in expected_dict.items():
            # k --》status_code nickName text v --》200 lemon_auto 账号或密码不正确
            # k就是我们要去断言的信息（响应状态码、响应体文本、响应体字段）
            if k == 'status_code':
                logger.info(f'响应状态码断言，预期结果:{v}，实际结果:{res.status_code}')
                assert res.status_code == v
            elif k == 'text':
                logger.info(f'响应体文本断言，预期结果:{v}，实际结果:{res.text}')
                assert res.text == v
            # 第三个分支我们要判断的是响应体字段断言，jsonpath表达式（它的固定开头就是$）-判断依据
            elif k[0] == '$':
                # 此时的k代表的就是jsonpath表达式
                actual = jsonpath.jsonpath(res.json(), k)[0]
                logger.info(f'响应字段:{k}断言，预期结果:{v}，实际结果:{actual}')
                assert actual == v
    else:
        logger.info('没有写断言，请补上')

# 封装一个统一处理数据库断言的函数
def assert_db(case_data):
    # 对列进行判空（判断Excel中是否有这列数据）
    if case_data.get('期望的数据库结果') == None:
        return
    # 取到【期望的数据库结果】
    expected_db = replace_by_mark(case_data['期望的数据库结果'])   #None
    logger.info('===========================数据库断言日志========================')
    # 转换为python字典
    expected_dic = json_convert_dict(expected_db)  # None
    if expected_dic:
    #if expected_dic != None:
        # k --> sql语句  v --> 期望值
        for k,v in expected_dic.items():
            # 执行sql语句
            actual = query_data(k,'one')[0]
            logger.info(f'查询的SQL语句:{k},预期结果:{v},实际结果:{actual}')
            assert actual == v
