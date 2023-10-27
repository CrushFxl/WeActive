# coding=utf-8

import os
import re
import shutil
import time
from configparser import ConfigParser
from threading import Thread
import colorama

import selenium
from cv2 import imread, QRCodeDetector
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

threads = []  # 线程池
tasks = []  # 任务队列
webTask = []  # WebTask对象列表


class WebTask:
    def __init__(self, img):
        self.browser = selenium.webdriver.Chrome(options=chrome_options)
        self.img_name = img
        self.url = ScanQRCode(img)
        self.name = None
        self.time = None
        self.state = self.GetName()
        self.GetTime()

    def GetName(self):
        try:
            self.browser.get(self.url)
        except:
            print(f"\033[;33;40m【错误】文件 [{self.img_name}] 二维码无法识别！已删除此任务。 \033[0m")
            return -2
        self.name = re.search(r"<title>(.*?)</title>", self.browser.page_source).groups()[0]
        matchOld = re.search(r"不能再接受新的答卷", self.browser.page_source)
        if matchOld:
            print(f"\033[;33;40m【错误】 [{self.name}] 已过期，无法填写！已删除此任务。\033[0m")
            return -1
        return 0

    def GetTime(self):
        scheTime = re.search(r"还有(\d+)天(\d+)时(\d+)分(\d+)秒", self.browser.page_source)
        if scheTime:
            d, h, m, s = scheTime.groups()
            self.time = int(d) * 86400 + int(h) * 3600 + int(m) * 60 + int(s)
        else:
            self.time = 0

    def Run(self):
        if self.state == 0:
            print(f"[{self.name}] 任务已加入计划。/ 计划刻：{self.time}")
            tasks.append(self.img_name)
            if self.time > 30:
                time.sleep(self.time - 30)
            print(f"[{self.name}] 开始执行。")
            self.FillForm()
            print(f"\033[0;32;40m[{self.name}] 已完成。\033[0m")
            self.EjectTask()

    def FillForm(self):
        while True:
            try:
                ques = self.browser.find_elements(By.CSS_SELECTOR, '[class="field ui-field-contain"]')
            except:
                print(f"\033[;33;40m【错误】 [{self.name}] 任务执行时出现错误！已删除此任务。\033[0m")
                break
            if len(ques) == 0:
                time.sleep(delay)
                self.browser.refresh()
                continue
            for que in ques:
                text = que.find_element(By.CSS_SELECTOR, '[class="topichtml"]').text
                type = que.find_elements(By.XPATH, 'child::*')[1].get_attribute('class')
                ans = MatchAnswer(text)
                if type == "ui-input-text" or type == "ui-input-text selfMess":
                    if ans:
                        que.find_element(By.TAG_NAME, 'input').send_keys(ans)
                    else:
                        print(f"\033[;33;40m【警告】[{self.name}] 无有效匹配项，任务切为手动模式...(60s)\033[0m")
                        self.state = 1
                else:
                    print(f"\033[;33;40m【警告】[{self.name}] 遇到未知的表单项，任务切为手动模式...(60s)\033[0m")
                    self.state = 1
            if self.state == 1:
                time.sleep(60)
            else:
                self.browser.find_element(By.CSS_SELECTOR, '[class="submitbtn mainBgColor"]').click()
            break

    def EjectTask(self):
        os.makedirs('./old/', exist_ok=True)
        shutil.move(f'./task/{self.img_name}', f'./old/{self.img_name}')
        tasks.remove(self.img_name)
        self.browser.quit()


def ScanQRCode(file_name):
    img = imread("./task/" + file_name)
    det = QRCodeDetector()
    url, pts, st_code = det.detectAndDecode(img)
    return url


def ReadSetting():
    conf = ConfigParser()
    conf.read('config.ini', encoding='utf-8')
    return float(conf['setting']['delay'])


def MatchAnswer(text):
    conf = ConfigParser()
    conf.read('config.ini', encoding='utf-8')
    for key, value in conf['answer'].items():
        if key in text:
            return value
    if conf.has_option("answer", "default"):
        return conf["answer"]["default"]
    else:
        return False


def ListenTask():
    while True:
        imgs = os.listdir(os.getcwd() + "/task/")
        for img in imgs:
            isNew = 1
            for task in tasks:
                if img == task:
                    isNew = 0
            if isNew:
                t = WebTask(img)
                webTask.append(t)
                thd = Thread(target=t.Run)
                threads.append(thd)
                thd.start()
        time.sleep(1)


def ListenCommand():
    while True:
        t = input()
        if t == "list":
            print("【当前计划任务】")
            for i in webTask:
                if i.img_name in tasks:
                    i.GetTime()
                    print(f" - {i.name} / 计划刻剩余：{i.time}秒")
        else:
            print("未知命令")


if __name__ == "__main__":
    delay = ReadSetting()
    colorama.init(autoreset=True)  # 自动调整print颜色样式编码
    chrome_options = selenium.webdriver.ChromeOptions()
    chrome_options.page_load_strategy = 'eager'
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    chrome_options.add_argument('log-level=3')
    Thread(target=ListenTask).start()  # 监听添加任务
    Thread(target=ListenCommand).start()  # 监听响应命令
    time.sleep(20)
    for thd in threads:  # 等待线程任务结束
        thd.join()
    print("\nGithub开源项目地址：https://github.com/CrushFxl/FormSubmitTool-based-on-wjx")
    print("作者：杭医CrushFxl  觉得程序好用？在项目页面上帮助作者点个Star吧！\n程序已结束.")
