"""
#用户名 : 17954
#日期 : 2023/4/10 11:12
"""
import requests
import logging
import warnings
from lxml import etree

warnings.filterwarnings('ignore')
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')

BASE_URL = 'http://www.ibiqu.org/xuanhuanxiaoshuo/'
headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.34'
}

def init():
    response = requests.get(url=BASE_URL, headers=headers)
    html = etree.HTML(response.text)
    li_list = html.xpath('//div[@class="r"]//li/span[@class="s2"]/a/@href')
    return li_list

def scrape_api(url):
    try:
        logging.info('scraping %s', url)
        response = requests.get(url, headers=headers)
        return response.text
    except requests.RequestException:
        logging.error('error occurred while scraping %s', url, exc_info=True)

from os import makedirs
from os.path import exists
result_dir = 'result'
exists(result_dir) or makedirs(result_dir)

def save(name, title, content):
    data_path = f'{result_dir}/{name}.txt'
    with open(data_path, mode='a', encoding='utf-8') as f:
        # 写入标题
        f.write(title)
        # 换行
        f.write('\n')
        # 写入小说内容
        f.write(content)

def parse_detail(name, url):
    html = scrape_api(url)
    html = etree.HTML(html)
    title = html.xpath('//div[@class="bookname"]/h1/text()')[0]
    print(title)
    content_list = html.xpath('//div[@id="content"]//p/text()')
    content_str = '\n'.join(content_list)
    save(name, title, content_str)

import time
def parse_text(html):
    html = etree.HTML(html)
    novel_name = html.xpath('//div[@id="info"]/h1/text()')[0]
    dd_list = html.xpath('//div[@id="list"]//dd/a/@href')[9:]
    for dd in dd_list:
        parse_detail(novel_name, dd)
    logging.info(novel_name, "saving successfully")


def main(urls):
        for url in urls:
            html = scrape_api(url)
            parse_text(html)

if __name__ == "__main__":
    novel_urls = init()
    main(novel_urls)

