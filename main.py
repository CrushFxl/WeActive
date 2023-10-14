# coding=utf-8
import time
from cv2 import imread, QRCodeDetector
from pyzbar import pyzbar
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By


def ScanQRCode(path):
    img = imread(path)
    det = QRCodeDetector()
    info, pts, st_code = det.detectAndDecode(img)
    return info


def MatchField(text):
    if text == "姓名":
        return "冯洋一"
    elif text == "班级":
        return "智医2301"
    elif text == "学号":
        return "6401230103"
    else:
        return "啥玩意"


if __name__ == "__main__":
    cnt = 0
    url = ScanQRCode(r"img.png")
    # url = "https://www.wjx.top/vm/ODYMYw5.aspx#"
    browser = Chrome()
    browser.get(url)
    # WebDriverWait(browser, 5).until(lambda d: "" in d.page_source)
    while True:
        FormCount = len(browser.find_elements(By.XPATH, '//*[@class="field ui-field-contain"]'))
        for i in range(1, FormCount + 1):
            text = browser.find_elements(By.XPATH, '//*[@class="topichtml"]')[i - 1].text
            ans = MatchField(text)
            browser.find_element(By.XPATH, f'//*[@id=\'q{i}\']').send_keys(ans)
        try:
            browser.find_element(By.XPATH, '//*[@class="submitbtn mainBgColor"]').click()  # 点击提交
        except:
            cnt += 1
            print(f"【失败】问卷尚未开始填写！（已尝试{cnt}次）")
            time.sleep(1)
            browser.refresh();
        else:
            print("【成功】问卷已提交。")
            break

    # headers = {  # 设定的浏览器请求头 "referer": "www.wjx.top", "cookie":
    # "acw_tc=76b20ffa16972569871175854e4f9c4e7ec6ce6ef98c44f8e9f1b119ec431e;
    # .ASPXANONYMOUS=7yIMCuc02gEkAAAAZTU0MjJiYzktYjgxYS00NzFlLWI4ZTEtODViNjE0MDVlZGU03s0TiCkPDHKtkg672YicYgUBRcU1;
    # Hm_lvt_21be24c80829bd7a683b2c536fcf520b=1697256989; jac238862082=31160712;
    # SERVERID=56bac570323aa451802d43d98d942ec7|1697257782|1697256987;
    # Hm_lpvt_21be24c80829bd7a683b2c536fcf520b=1697257784", "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)
    # AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36 Edg/117.0.2045.60" } res = requests.get(
    # url=url, headers=headers).text print(res)
