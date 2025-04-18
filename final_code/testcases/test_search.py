import pytest
from common.base_test import read_excel,execute_case
from common.path_util import exceldata_path
case_datas = read_excel(exceldata_path, '搜索商品接口')


@pytest.mark.parametrize('case_data', case_datas)
def test_search(case_data):
    execute_case(case_data)


