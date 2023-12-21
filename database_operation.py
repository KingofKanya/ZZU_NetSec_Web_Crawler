import mysql.connector


def delete_table(tablename):
    # 连接数据库
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='passport',
        database='crawler'
    )

    # 创建一个游标对象
    cursor = conn.cursor()

    # 删除news表中的所有数据
    delete_query = f"DELETE FROM {tablename}"
    cursor.execute(delete_query)

    # 提交更改并关闭连接
    conn.commit()
    cursor.close()
    conn.close()

    print(f"{tablename} table 数据删除完毕")


def save_to_database(data_list,p):
    # 连接数据库
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='passport',
        database='crawler'
    )

    # 创建一个游标对象
    cursor = conn.cursor()

    # 假设你的数据存储在名为p的表中，根据你的实际情况修改表名和字段
    insert_query = f"INSERT INTO {p} (id, show_time, title) VALUES (%s, %s, %s)"

    # 将数据插入数据库
    for item in data_list:
        values = (item['id'], item['show_time'], item['title'])
        cursor.execute(insert_query, values)

    # 提交更改并关闭连接
    conn.commit()
    cursor.close()
    conn.close()


def read_news_from_database(p):
    # 连接数据库
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='passport',
        database='crawler'
    )

    # 创建一个游标对象
    cursor = conn.cursor()

    # 查询p表中的所有数据
    select_query = f"SELECT * FROM {p}"
    cursor.execute(select_query)

    ret = cursor.fetchall()

    # 关闭连接
    cursor.close()
    conn.close()

    return ret

