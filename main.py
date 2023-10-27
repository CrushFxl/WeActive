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
tasks = {}  # 任务队列 {文件名:WebTask对象}


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
        try:
            scheTime = re.search(r"还有(\d+)天(\d+)时(\d+)分(\d+)秒", self.browser.page_source)
            d, h, m, s = scheTime.groups()
            self.time = int(d) * 86400 + int(h) * 3600 + int(m) * 60 + int(s)
        except:
            self.time = -1

    def Run(self):
        if self.state == 0:
            print(f"[{self.name}] 任务已加入计划。| 计划刻：{self.time}")
            if self.time > 30:
                time.sleep(self.time - 30)
            print(f"[{self.name}] 开始执行。")
            self.FillForm()
            print(f"\033[0;32;40m[{self.name}] 已完成。\033[0m")
        self.EjectTask()  # 销毁该计划任务

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
                        print(f"\033[;33;40m【警告】[{self.name}] 无有效匹配，等待手动填写...(60s)\033[0m")
                        self.state = 1
                else:
                    print(f"\033[;33;40m【警告】[{self.name}] 遇到未知表单，等待手动填写...(60s)\033[0m")
                    self.state = 1
            if self.state == 1:
                time.sleep(60)
            else:
                self.browser.find_element(By.CSS_SELECTOR, '[class="submitbtn mainBgColor"]').click()
            break

    def EjectTask(self):
        os.makedirs('./old/', exist_ok=True)
        shutil.move(f'./task/{self.img_name}', f'./old/{self.img_name}')
        tasks.pop(self.img_name)    # 从任务队列中弹出
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
            for task in tasks.keys():
                if img == task:
                    isNew = 0
            if isNew:
                tasks[img] = WebTask(img)   # 创建任务实例并添加到计划任务队列
                thrd = Thread(target=tasks[img].Run)    # 创建线程
                threads.append(thrd)    # 加入到线程池
                thrd.start()
        time.sleep(1)


def ListenCommand():
    while True:
        msg = input()
        if msg == "list":
            for t in tasks.values():    # 遍历当前任务对象
                t.GetTime()
                print(f" - {t.name} | 计划刻：{t.time}")
            print()
        else:
            print("[未知命令]")


if __name__ == "__main__":
    delay = ReadSetting()
    colorama.init(autoreset=True)  # 自动调整print颜色样式编码
    chrome_options = selenium.webdriver.ChromeOptions()
    chrome_options.page_load_strategy = 'eager'
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    Thread(target=ListenTask).start()  # 监听添加任务
    Thread(target=ListenCommand).start()  # 监听响应命令
    print("\nGithub开源项目地址：https://github.com/CrushFxl/FormSubmitTool-based-on-wjx")
    print("作者：杭医CrushFxl  觉得好用吗？在项目页面上帮助作者点个Star吧！")
    for thd in threads:  # 等待线程任务结束
        thd.join()
