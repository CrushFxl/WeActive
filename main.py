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
tasks = []  # 任务池


class WebTask:
    def __init__(self, img):
        self.browser = selenium.webdriver.Chrome(options=chrome_options)
        self.img_name = img
        self.url = ScanQRCode(img)
        self.name = None
        self.time = None
        self.state = None
        self.GetBasicInfo()

    def GetBasicInfo(self):
        try:
            self.browser.get(self.url)
        except:
            self.state = -2
            return
        page = self.browser.page_source
        self.name = re.search(r"<title>(.*?)</title>", page).groups()[0]
        matchOld = re.search(r"不能再接受新的答卷", page)
        matchTime = re.search(r"距离开始还有(\d+)天(\d+)时(\d+)分(\d+)秒", page)
        if matchOld:
            self.state = -1

        if matchTime:
            d, h, m, s = matchTime.groups()
            self.time = int(d) * 86400 + int(h) * 3600 + int(m) * 60 + int(s)
            self.name = re.search(r"\"htitle\">(.*?)<", page).groups()[0]
            self.state = 0
        else:
            self.state = 1

    def FillForm(self, que):
        # num = que.get_attribute('topic')
        text = que.find_element(By.CSS_SELECTOR, '[class="topichtml"]').text
        type = que.find_elements(By.XPATH, 'child::*')[1].get_attribute('class')
        ans = MatchAnswer(text)
        if type == "ui-input-text" or type == "ui-input-text selfMess":
            if ans:
                que.find_element(By.TAG_NAME, 'input').send_keys(ans)
            else:
                print(f"\033[;33;40m【警告】[{self.name}] 无有效匹配项，等待手动提交...(60s)\033[0m")
                self.state = 2
        else:
            print(f"\033[;33;40m【警告】[{self.name}] 遇到未知的表单项，等待手动提交...(60s)\033[0m")
            self.state = 2

    def Execute(self):
        if self.state == -2:
            print(f"\033[;33;40m【错误】文件 [{self.img_name}] 二维码无法识别！已删除此任务。 \033[0m")
            self.EjectTask()
            return
        elif self.state == -1:
            print(f"\033[;33;40m【错误】 [{self.name}] 已过期，无法填写！已删除此任务。\033[0m")
            self.EjectTask()
            return
        elif self.state == 1:
            print(f"\033[;33;40m【警告】 [{self.name}] 已开放填写，提交可能不及时！\033[0m")
        else:
            print(f"[{self.name}] 任务已加入计划。/ 计划刻：{self.time}")
            if self.time > 30:
                time.sleep(self.time - 30)
        print(f"[{self.name}] 开始执行。")
        while True:
            try:
                ques = self.browser.find_elements(By.CSS_SELECTOR, '[class="field ui-field-contain"]')
            except:
                print(f"\033[;33;40m【错误】 [{self.name}] 任务执行时出现错误！已删除此任务。\033[0m")
                self.state = -3
                break
            if len(ques) == 0:
                time.sleep(delay)
                self.browser.refresh()
                continue
            for que in ques:
                self.FillForm(que)
            self.browser.find_element(By.CSS_SELECTOR, '[class="submitbtn mainBgColor"]').click()
            if self.state == 2:
                time.sleep(60)
            break
        if self.state >= 0:
            print(f"\033[0;32;40m[{self.name}] 已完成。\033[0m")
        self.EjectTask()

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
                tasks.append(img)
                thd = Thread(target=t.Execute)
                threads.append(thd)
                thd.start()
        time.sleep(1)


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


if __name__ == "__main__":
    delay = ReadSetting()
    colorama.init(autoreset=True)   # 自动调整print颜色样式编码
    chrome_options = selenium.webdriver.ChromeOptions()
    chrome_options.page_load_strategy = 'eager'
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    chrome_options.add_argument('log-level=3')
    Thread(target=ListenTask).start()  # 监听添加任务
    time.sleep(20)
    for thd in threads:  # 等待线程任务结束
        thd.join()
    print("\nGithub开源项目地址：https://github.com/CrushFxl/FormSubmitTool-based-on-wjx")
    print("作者：杭医CrushFxl  觉得程序好用？在项目页面上帮助作者点个Star吧！")
    print("程序已结束.")
