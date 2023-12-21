import requests

if __name__ == '__main__':
    url_news = "http://softschool.zzu.edu.cn/front/detail?typeId=4028d3826efcc0fd016efcc7ccce0001"
    url_announcement = "http://softschool.zzu.edu.cn/front/detail?typeId=4028d3826efcc0fd016efcc9b70b0002"
    url = "http://softschool.zzu.edu.cn/front/article/findArticleDetailList"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/119.0.0.0 Safari/537.36'
    }
    params = {
        "typeId": "4028d3826efcc0fd016efcc7ccce0001",
        "currentPage": "1"
    }
    response = requests.post(url=url, params=params, headers=headers)
    print(response.text)

    response_json = response.json()
    total_page = response_json["page"]["total"]
    print(total_page)

    print('over')
    # 从0开始
    first_news_url_id = response_json["page"]["data"][0]["id"]
    print(first_news_url_id)
    first_news_url = "http://softschool.zzu.edu.cn/front/singleArticleDetail"
    p2 = {
        "id": first_news_url_id
    }
    response2 = requests.post(url=first_news_url, params=p2, headers=headers)
    fp = open("./data/a.html", "w", encoding="utf-8")
    fp.write(response2.text)

    # 获取文章内容
    url_text = "http://softschool.zzu.edu.cn/front/article/getSingleArticleDetail"
    # 两个id应该是一样的
    response3 = requests.post(url=url_text, params=p2, headers=headers)

    the_html_content = response3.json()["content"]
    # 处理页面中的img,	http://softschool.zzu.edu.cn/file/showFile?fileId=4a453ec88ba53d71018c582400b60206
    p=the_html_content.replace("/file/showFile", "http://softschool.zzu.edu.cn/file/showFile")

    fp = open("./data/b.html", "w", encoding="gbk")
    # 在content中,返回的也是json,而且还用gbk编码,不是utf-8
    fp.write(p)
