import pytest
from common.base_test import execute_case,read_excel
from common.path_util import exceldata_path
case_datas = read_excel(exceldata_path, '登录接口')

@pytest.mark.parametrize('case_data', case_datas)
def test_login(case_data):
    execute_case(case_data)
