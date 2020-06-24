import requests
import re
import urllib
from bs4 import BeautifulSoup

# 详情页url队列
detail_urls = set()

# 通用网页下载器
def download(url, timeout=5, user_agent="htaseospider", proxy=None, num_retries=5):
    headers = {"User-Agent":user_agent}
    request = requests.get(url, headers=headers)
    request.encoding = 'utf-8'
    print ("Downloading:",url)
    try:
        html = request.text
    except:
        html = None
        if num_retries > 0:
            return download(url, timeout, user_agent, proxy, num_retries-1)
    return html

# 获取详情页url列表
def extract_list(query, html):
     global detail_urls
     soup = BeautifulSoup(html, 'html.parser')
     for url_item in soup.select('.excerpt h2 a'):
        durl = url_item['href']
        detail_urls.add(urllib.parse.urljoin(query,durl))

# 获取详情页标题和内容
def extract_detail(html):
    content = ""
    content_block = re.search(r'<article class="article-content">(.*?)<div class="article-tags">', html, re.S)
    if content_block:
        content_block = content_block.group(1)
    else:
        content_block = ""
    has_title = re.search(r'<h1 class="article-title">(.*?)</h1>', html, re.S)
    title = has_title.group(1) if has_title else ""
    ptag_list = re.findall(r'(<p style="font-size:15px;">.*?</p>)', content_block, re.S)
    for line in ptag_list[:-1]:
        line = re.sub(r'<a.*?>(.*?)</a>', '\g<1>', line)
        content += line
    return {"title":title, "content":content}

# 保存结果
def save_file(result, model=True, single=None):
    if model:
        filename = "cpsassb/%s.txt" % result["title"]
        with open(filename, 'w') as f:
            line = "%s###%s\n" % (result["title"], result["content"])
            f.write(line)
            f.flush()
    else:
        if single is None:
            print ("请传入保存结果的文件对象")
            return
        line = "%s###%s\n" % (result["title"], result["content"])
        single.write(line)
        single.flush()

# 列表页爬虫
def list_spider(pagenum):
    for pn in range(1, pagenum+1):
        list_url = "http://www.cpsassb.com/yangya/list_20_{}.html".format(pn)
        source = download(list_url)
        if source is None:
            print ("获取列表页源码失败", list_url)
            continue
        else:
            extract_list(list_url, source)
    print ("列表页爬虫执行完毕")

# 详情页爬虫
def detail_spider(single=None):
    global detail_urls
    while detail_urls:
        durl = detail_urls.pop()
        source = download(durl)
        if source is None:
            print ("获取详情页源码失败", durl)
            continue
        else:
            content_dict = extract_detail(source)
            model = False if single else True
            save_file(content_dict, model=model, single=single)
    print ("详情页爬虫执行完毕")


if __name__ == "__main__":
    save = open("cpsassb.txt", 'a')
    list_spider(5)
    detail_spider(save)
    save.close()
    print ("Done")
