# coding=utf-8

import time
import os
import re
import selenium
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from cv2 import imread, QRCodeDetector
from configparser import ConfigParser

cnt = 1


class WebTask:
    def __init__(self, img):
        self.browser = selenium.webdriver.Chrome()
        self.url = self.ScanQRCode(img)
        self.name = None
        self.time = None
        self.state = None
        self.GetBasicInfo()

    def GetBasicInfo(self):
        self.browser.get(self.url)
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
        print(self.name)

    @staticmethod
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


def FillForm(que):
    #  num = que.get_attribute('topic')
    text = que.find_element(By.CSS_SELECTOR, '[class="topichtml"]').text
    type = que.find_elements(By.XPATH, 'child::*')[1].get_attribute('class')
    ans = MatchAnswer(text)
    if type == "ui-input-text" or type == "ui-input-text selfMess":
        if ans:
            que.find_element(By.TAG_NAME, 'input').send_keys(ans)
        else:
            print("【WARNING】无有效匹配项且无缺省匹配，已跳过填写。")
    else:
        print("【WARNING】遇到未知的表单类型，已跳过填写。")


if __name__ == "__main__":
    delay = ReadSetting()
    chrome_options = Options()
    chrome_options.page_load_strategy = 'eager'
    path = os.getcwd() + "/task/"  # 程序下绝对路径
    imgs = os.listdir(path)  # 文件名列表
    for img in imgs:
        t = WebTask(img)

        # match = re.search(r"不能再接受新的答卷", browser.page_source)

    #  url = "https://www.wjx.cn/vm/evfoZuA.aspx#"
    # while True:
    #     ques = browser.find_elements(By.CSS_SELECTOR, '[class="field ui-field-contain"]')
    #     if len(ques) == 0:
    #         time.sleep(delay)
    #         browser.refresh()
    #         continue
    #     for que in ques:
    #         FillForm(que)
    #     browser.find_element(By.CSS_SELECTOR, '[class="submitbtn mainBgColor"]').click()
    #     break
    # print("【INFO】计划任务已执行，60秒后将关闭网页...")
    # print("Github开源项目地址：https://github.com/CrushFxl/FormSubmitTool-based-on-wjx")
    # print("作者：杭医CrushFxl 程序仅供学习交流使用，切勿作其他用途。")
    # time.sleep(60)
