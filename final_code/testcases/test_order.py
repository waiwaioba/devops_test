import json

import jsonpath
import pytest
from common.base_test import execute_case,read_excel
from common.path_util import exceldata_path
case_datas = read_excel(exceldata_path, '下单流程')


@pytest.mark.parametrize('case_data', case_datas)
def test_order(case_data):
    execute_case(case_data)

