from pathlib import Path
# 这个模块是用来专门处理文件路径问题
# 1、excel文件
exceldata_path = Path(__file__).parent.parent / 'data' / 'casedata.xlsx'
# 2、日志文件
log_path = Path(__file__).parent.parent / 'outputs' / 'log' / 'api_auto.log'
# 3、报告路径
report_path = Path(__file__).parent.parent / 'outputs' / 'allure-results'