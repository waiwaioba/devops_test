# 数据库相关操作的公共的模块封装
import faker
import pymysql
from faker import Faker


# 连接数据库
def connect_db():
    conn = pymysql.connect(
        host='mall.lemonban.com',
        port=3306,
        user='lemon_auto',
        password='lemon!@123',
        database='yami_shops',
        charset='utf8'
    )
    return conn

# 查询数据库的函数封装
def query_data(sql,type):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(sql)
    result = None
    if type == 'one':   #自动化测试的时候这个函数用的最多
        result = cursor.fetchone()
    elif type == 'all':
        result = cursor.fetchall()
    elif type == 'many':
        result = cursor.fetchmany()
    else:
        return '你所写的type参数不支持'
    conn.close()
    return result

# 增加数据函数封装
# 删除数据函数封装

# 封装函数用于获取未注册的随机手机号码
def get_unregister_phone():
    faker = Faker(locale='zh-CN')
    while True:
        # 1、生成一个合法的手机号码
        phone = faker.phone_number()
        sql = f'select count(*) from tz_user where user_mobile = "{phone}"'
        # 2、判断手机号码是否在数据库中存在 result 结果为0或者1
        result = query_data(sql, 'one')[0]
        if result == 0:
            # 号码符合要求
            break
    return phone

# 封装函数用于获取未注册的随机用户名
def get_unregister_username():
    faker = Faker(locale='zh-CN')
    while True:
        # 1、生成一个合法的用户名
        username = faker.user_name()
        sql = f'select count(*) from tz_user where user_name = "{username}"'
        # 2、判断用户名是否在数据库中存在 result 结果为0或者1
        result = query_data(sql, 'one')[0]
        # 还需要加上对于用户名长度的判断：满足4-16位
        if result == 0 and 4<=len(username)<=16:
            # 用户名符合要求
            break
    return username