import requests
import os
import database_operation

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


def get_list_number(url, params):
    response = requests.post(url=url, params=params, headers=headers)
    response_json = response.json()
    list_number = response_json["page"]["total"]
    return list_number


def choose(p):
    if p == 'news':
        return news_url, news_params
    elif p == 'announcements':
        return announcements_url, announcements_params


def save_id(p):
    url, params = choose(p)
    print(f"------开始保存学院{p} id------")
    database_operation.delete_table(p)
    list_number = get_list_number(url, params)
    page_number = list_number // pageSize
    print(f"总共有{page_number}页,共{list_number}个{p}")
    for currentPage in range(1, page_number + 1):
        params["currentPage"] = currentPage
        resp = requests.post(url=url, params=params, headers=headers)
        resp_json = resp.json()
        data_list = resp_json["page"]["data"]
        database_operation.save_to_database(data_list, p)
        print(f"第{currentPage}页数据保存完毕")
    print(f"------学院{p} id保存完毕------")


def save_page(p):
    url = "http://softschool.zzu.edu.cn/front/article/getSingleArticleDetail"
    directory = f"./{p}/"
    # 检查目录是否存在，如果不存在则创建
    if not os.path.exists(directory):
        os.makedirs(directory)
    print(f"------开始保存学院{p}页面------")
    i = 1
    # 逐条读取数据
    for row in database_operation.read_news_from_database(p):
        # row是一个元组，包含了每条数据的各个字段值
        id, show_time, title = row  # python中的unpacking操作
        resp = requests.post(url=url, params={
            "id": id,
        }, headers=headers)
        # 处理页面中的img,	http://softschool.zzu.edu.cn/file/showFile?fileId=4a453ec88ba53d71018c582400b60206
        content = resp.json()["content"].replace("/file/showFile", "http://softschool.zzu.edu.cn/file/showFile")
        fp = open(f"./{p}/{p}{i}.html", "a", encoding="utf-8")
        fp.write(f"<h1>{title}</h1><br><h3>{show_time}</h3><meta charset=\"UTF-8\">")
        fp.write(content)
        print(f"第{i}个页面保存完毕")
        i = i + 1
    print(f"------学院{p}页面保存完毕------")


def get_all(p):
    save_id(p)
    save_page(p)


if __name__ == '__main__':
    get_all("news")
    get_all("announcements")
