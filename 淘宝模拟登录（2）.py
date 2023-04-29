"""
#用户名 : 17954
#日期 : 2023/4/29 13:09
"""
import pickle
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os

class taobao:
    def __init__(self):
        # 去除浏览器识别
        self.option = Options()
        self.option.add_experimental_option('excludeSwitches', ['enable-automation'])
        self.option.add_experimental_option("detach", True)

        self.browser = webdriver.Chrome(options=self.option)
        self.url = 'http://www.taobao.com'
        # 最大化窗口
        self.browser.maximize_window()
        # 智能等待，在设置时间范围内，只要条件成立，马上结束等待, implicitly_wait
        # 等待一旦设置，那么这个等会在浏览器对象的整个生命周期起作用
        self.browser.implicitly_wait(5)

    def load_cookies(self, cookies_file):
        if os.path.exists(cookies_file):
            with open(cookies_file, 'rb') as f:
                cookies = pickle.load(f)
                for cookie in cookies:
                    self.browser.add_cookie(cookie)
                return True
        return False

    def manual_login(self, cookies_file):
        input("请登录，登录成功跳转后，按回车键继续...")
        with open(cookies_file, 'wb') as f:
            pickle.dump(self.browser.get_cookies(), f)
        print("程序正在继续运行")

    def login(self):
        self.browser.get(self.url)
        cookies_file = 'cookies.pkl'
        if not self.load_cookies(cookies_file):
            self.manual_login(cookies_file)
            self.load_cookies(cookies_file)
        self.browser.get(self.url)
        nick_name = self.browser.find_element(By.CLASS_NAME, 'site-nav-user').text
        if nick_name:
            print('登录成功，呢称为:' + nick_name)
        else:
            print('登录出错')

if __name__ == "__main__":
    tb = taobao()
    tb.login()