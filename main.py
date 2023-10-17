# coding=utf-8
import time
import selenium
from selenium.webdriver.common.by import By
from cv2 import imread, QRCodeDetector
from configparser import ConfigParser


def ScanQRCode(path):
    img = imread(path)
    det = QRCodeDetector()
    info, pts, st_code = det.detectAndDecode(img)
    return info


def GetAnswer(text):
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
    # num = que.get_attribute('topic')
    text = que.find_element(By.CSS_SELECTOR, '[class="topichtml"]').text
    type = que.find_elements(By.XPATH, 'child::*')[1].get_attribute('class')
    if type == "ui-input-text":
        ans = GetAnswer(text)
        if ans:
            que.find_element(By.TAG_NAME, 'input').send_keys(ans)
        else:
            print("【WARNING】无有效匹配项且无缺省匹配，已跳过填写。")
    else:
        print("【WARNING】遇到未知的表单类型，已跳过填写。")


if __name__ == "__main__":
    cnt = 1
    delay = 0.5
    # url = ScanQRCode(r"10171030.png")
    url = "https://www.wjx.cn/vm/evfoZuA.aspx# "
    browser = selenium.webdriver.Chrome()
    browser.get(url)
    while True:
        ques = browser.find_elements(By.CSS_SELECTOR, '[class="field ui-field-contain"]')
        if len(ques) == 0:
            print(f"【WARNING】无可填项，问卷可能未开放。 #{cnt}")
            cnt += 1
            time.sleep(delay)
            browser.refresh()
            continue
        for que in ques:
            FillForm(que)
        browser.find_element(By.CSS_SELECTOR, '[class="submitbtn mainBgColor"]').click()  # 点击提交
        break
    print("【INFO】计划任务已执行，60秒后将关闭网页...")
    time.sleep(60)
