"""
#用户名 : 17954
#日期 : 2023/4/18 17:25
"""
# https://cmse.sdust.edu.cn/index/xyxw.htm
from pyppeteer import launch
from pyppeteer.errors import TimeoutError
import asyncio
import aiohttp
import aiofiles
import logging
import warnings
warnings.filterwarnings('ignore')
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')

BASE_URL = 'https://cmse.sdust.edu.cn/index/xyxw/{page}.htm'
MAX_PAGE = 6
TIME_OUT = 10
width, height = 1366, 768
args = ['--disable-infobars', f'--window-size={width}, {height}']
browser, tab = None, None

async def init():
    global browser, tab
    browser = await launch(headless=False, args=args)
    tab = await browser.newPage()
    await tab.setViewport({'width': width, 'height': height})

import time
async def scrape_api(url, selector):
    try:
        logging.info('scraping %s', url)
        await tab.goto(url)
        await tab.waitForSelector(selector, options={'timeout': TIME_OUT * 1000})
    except TimeoutError:
        logging.error('error occurred while scraping %s', url, exc_info=True)

async def scrape_detail_urls(url):
    await scrape_api(url, '#list ul')

import re
detail_datas = []
async def scrape_detail(url):
    await scrape_api(url, 'form')
    show_title = await tab.querySelectorEval('form #show_title', 'node => node.innerText')
    text = await tab.querySelectorEval('form #show_info', 'node => node.innerText')
    p1 = re.compile(r'(\d+-\d+-\d+)', re.S)
    publish_time = re.findall(p1, text)[0]
    click = await tab.querySelectorEval('form #show_info span', 'node => node.innerText')
    detail_data = {
        "新闻标题": show_title,
        "发行时间": publish_time,
        "点击量": click,
    }
    detail_datas.append(detail_data)

detail_urls = []
async def parse_detail_urls():
    global detail_urls
    urls = await tab.querySelectorAllEval('#list ul li a', 'nodes => nodes.map(node => node.href)')
    for url in urls:
        # 该网页中有几个与别的url不同的url，得过滤掉
        if '/info' in url and '1034/14862' not in url and '1034/14769' not in url:
            url = url.replace('../../', 'https://cmse.sdust.edu.cn/')
            detail_urls.append(url)

async def main():
    await init()
    try:
        for page in range(1, MAX_PAGE + 1):
            url = BASE_URL.format(page=page)
            await scrape_detail_urls(url)
            await parse_detail_urls()

        # 第一页单独爬取
        await scrape_detail_urls('https://cmse.sdust.edu.cn/index/xyxw.htm')
        await parse_detail_urls()

        for url in detail_urls:
            await scrape_detail(url)
        print(detail_datas)
    except Exception as e:
        logging.error(f"{e}")
    finally:
        browser.close()

import csv
def save_csv():
    with open('新闻数据.csv', mode='w', newline='', encoding='utf-8-sig') as f:
        fieldnames = ['新闻标题', '发行时间', '点击量']
        write = csv.DictWriter(f, fieldnames=fieldnames)
        write.writeheader()
        for row in detail_datas:
            write.writerow(row)

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
    save_csv()