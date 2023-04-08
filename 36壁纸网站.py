"""
#用户名 : 17954
#日期 : 2023/4/7 19:20
"""
# 爬取36壁纸网站 https://www.3gbizhi.com/
from pyppeteer import launch
from pyppeteer.errors import TimeoutError
import asyncio
import aiohttp
import aiofiles
import logging
import warnings

warnings.filterwarnings('ignore')
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')

BASE_URL = 'https://www.3gbizhi.com/sjbz/index_{page}.html'
MAX_PAGE = 4
TIME_OUT = 10
width, height = 1366, 768
args = ['--disable-infobars', f'--window-size={width}, {height}']
browser, tab = None, None

async def init():
    global browser, tab
    browser = await launch(headless=False, args=args)
    tab = await browser.newPage()
    await tab.setViewport({'width': width, 'height': height})

async def scrape_api(url, selector):
    try:
        logging.info('scraping %s', url)
        await tab.goto(url)
        await tab.waitForSelector(selector, options={'timeout': TIME_OUT * 1000})
    except TimeoutError:
        logging.error('error occurred while scraping %s', url, exc_info=True)

async def scrape_detail_one(url):
    await scrape_api(url, '.imgw')

async def scrape_detail_two(url):
    await scrape_api(url, '.showtitle')
    image_url = await tab.querySelectorEval('.morew a', 'node => node.href')
    name = await tab.querySelectorEval('.showtitle h2', 'node => node.innerText')
    return {
        "image_url": image_url,
        "name": name,
    }

from os import makedirs
from os.path import exists

result_dir = 'Picture'
exists(result_dir) or makedirs(result_dir)
async def save_img(data):
    name = data.get('name')
    url = data.get('image_url')
    logging.info(f'{url}正在下载')
    data_path = f'{result_dir}/{name}.jpg'
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as res:
            content = await res.content.read()
            async with aiofiles.open(data_path, 'wb') as f:
                await f.write(content)
    logging.info(f'{name}下载成功！！')

datas = []
async def parse_detail():
    global datas
    detail_urls = await tab.querySelectorAllEval('.cl .imgw', 'nodes => nodes.map(node => node.href)')
    for url in detail_urls:
        result = await scrape_detail_two(url)
        datas.append(result)

async def main():
    await init()
    try:
        for page in range(1, MAX_PAGE + 1):
            url = BASE_URL.format(page=page)
            await scrape_detail_one(url)
            await parse_detail()

        scrape_img_tasks = [asyncio.ensure_future(save_img(data)) for data in datas]
        await asyncio.gather(*scrape_img_tasks)
    except Exception as e:
        logging.error(f"{e}")
    finally:
        browser.close()

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())