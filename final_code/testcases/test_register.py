import json

import jsonpath
import pytest
from common.base_test import read_excel,execute_case
from common.path_util import exceldata_path
from common.db_util import get_unregister_phone,get_unregister_username,query_data
from common.base_test import env_dict

case_datas = read_excel(exceldata_path, '注册流程')

# 在用例运行之前，我们需要获取到未注册的手机号码与用户名,将其保存到环境变量中
phone = get_unregister_phone()
username = get_unregister_username()
env_dict['phone'] = phone
env_dict['username']=username

# 问题：怎么往环境变量中存储验证码数据，而且需要等到第一条接口运行完之后才会在数据库中生成短信验证码信息

@pytest.mark.parametrize('case_data', case_datas)
def test_register(case_data):
    execute_case(case_data)
    # 在第一条接口执行完毕之后获取验证码数据
    if case_data['编号'] == 1:
        sql = f'select mobile_code from tz_sms_log where user_phone = {phone} order by rec_date desc limit 1;'
        mobile_code = query_data(sql, 'one')[0]
        env_dict['mobile_code'] = mobile_code
