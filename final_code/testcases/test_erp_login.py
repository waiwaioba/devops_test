import pytest
from common.base_test import assert_res,read_excel,send_request
from common.path_util import exceldata_path

case_datas = read_excel(exceldata_path, 'erp项目测试form表单传参')


@pytest.mark.parametrize('case_data', case_datas)
def test_login(case_data):
    res = send_request(case_data)
    assert_res(case_data, res)


