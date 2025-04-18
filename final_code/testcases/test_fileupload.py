import pytest
from common.base_test import assert_res ,read_excel,send_request
from common.path_util import exceldata_path
case_datas = read_excel(exceldata_path, '文件上传接口')

@pytest.mark.parametrize('case_data', case_datas)
def test_upload(case_data):
    res = send_request(case_data)
    assert_res(case_data, res)
