import requests
import os
import database_operation
import time
import multiprocessing
import threading

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/119.0.0.0 Safari/537.36'
}
news_url = "http://softschool.zzu.edu.cn/front/article/findArticleDetailList"
announcements_url = "http://softschool.zzu.edu.cn/front/article/findArticleDetailList"
news_params = {
    "typeId": "4028d3826efcc0fd016efcc7ccce0001",
    "pageSize": "10",
    "currentPage": "1",
}
announcements_params = {
    "typeId": "4028d3826efcc0fd016efcc9b70b0002",
    "pageSize": "10",
    "currentPage": "1",
}
pageSize = 10
# i用来记录是第几条
i = 1


def get_list_number(url, params):
    """

    :param url:
    :param params:
    :return: 返回请求响应中的所有数据的json串
    """
    response = requests.post(url=url, params=params, headers=headers)
    response_json = response.json()
    list_number = response_json["page"]["total"]
    return list_number


def choose(p):
    """
    根据p来返回对应的url和params
    :param p:
    :return:
    """
    if p == 'news':
        return news_url, news_params
    elif p == 'announcements':
        return announcements_url, announcements_params


def add_to_database(url, params, p, current_page):
    """
    将current_page页上的所有数据存入到对应数据库
    :param url:
    :param params:
    :param p:
    :param current_page:
    :return:
    """
    params["currentPage"] = current_page
    resp = requests.post(url=url, params=params, headers=headers)
    resp_json = resp.json()
    data_list = resp_json["page"]["data"]
    database_operation.save_to_database(data_list, p)
    print(f"{p}第{current_page}页数据保存完毕")


def save_id(p):
    """
    将每个页面的基本信息存入数据库,供save_page使用
    :param p:
    :return:
    """
    url, params = choose(p)
    print(f"------开始保存学院{p} id------")
    # 删除数据库table中的所有数据
    database_operation.delete_table(p)
    list_number = get_list_number(url, params)
    page_number = list_number // pageSize
    if list_number % page_number != 0:
        page_number += 1
    print(f"{p}总共有{page_number}页,共{list_number}个{p}")
    threads = []

    # 使用多线程
    # page_number会向下取整,所以要+1确保能取出最后一页的信息
    for currentPage in range(1, page_number + 1):
        threads.append(
            threading.Thread(target=add_to_database, args=(url, params, p, currentPage,))
        )

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    print(f"------学院{p} id保存完毕------")


def save_html(row, url, p):
    """
    保存网页的html
    :param row:
    :param url:
    :param p:
    :return:
    """
    global i
    # row是一个元组，包含了每条数据的各个字段值
    id, show_time, title = row  # python中的unpacking操作
    resp = requests.post(url=url, params={
        "id": id,
    }, headers=headers)
    # 服务器会返回502,过载,添加重试机制
    max_retries = 3
    retry_count = 0
    while resp.status_code != 200 and retry_count < max_retries:
        print(f"{p} 的第 {i} 条重试中... 第 {retry_count + 1} 次重试")
        time.sleep(5)  # 可以根据需要调整等待时间
        resp = requests.post(url=url, params={"id": id}, headers=headers)
        retry_count += 1

    # 抓取来的html源码
    content = ''
    if resp.status_code == 200:
        # 处理页面中的img,加上资源前缀	http://softschool.zzu.edu.cn/file/showFile?fileId=4a453ec88ba53d71018c582400b60206
        content = resp.json()["content"].replace("/file/showFile", "http://softschool.zzu.edu.cn/file/showFile")
    else:
        print(f"请求错误，状态码: {resp.status_code}")

    fp = open(f"./{p}/{p}{i}.html", "a", encoding="utf-8")
    # 添加html头,制定渲染字符集为utf-8
    fp.write(f"<h1>{title}</h1><br><h3>{show_time}</h3><meta charset=\"UTF-8\">")
    fp.write(content)
    print(f"{p}第{i}个页面保存完毕")
    i = i + 1


def save_page(p):
    """

    :param p:
    :return:
    """
    global i
    url = "http://softschool.zzu.edu.cn/front/article/getSingleArticleDetail"
    directory = f"./{p}/"
    # 检查目录是否存在，如果不存在则创建目录
    if not os.path.exists(directory):
        os.makedirs(directory)
    print(f"------开始保存学院{p}页面------")
    i = 1
    # 逐条读取数据
    rows = database_operation.read_from_database(p)
    threads = []
    for row in rows:
        threads.append(
            threading.Thread(target=save_html, args=(row, url, p))
        )
    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()
    print(f"------学院{p}页面保存完毕------")


def get_all(p):
    """
    爬取p的所有网页
    :param p:
    :return:
    """
    save_id(p)
    save_page(p)


def execute_with_time(func, arg):
    """
    打印news和announcements各自进程的执行时间,并执行各自方法
    :param func:
    :param arg:
    :return:
    """
    start_time = time.time()
    func(arg)
    end_time = time.time()
    execution_time = end_time - start_time
    print(f"{arg} 的 {func.__name__} 方法执行了 {execution_time} 秒")


if __name__ == '__main__':
    processes = []
    categories = ["news", "announcements"]

    # 使用多进程
    for category in categories:
        process = multiprocessing.Process(target=execute_with_time, args=(get_all, category))
        processes.append(process)
        process.start()

    for process in processes:
        process.join()
