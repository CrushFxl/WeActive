# coding=utf-8
import time
import selenium
from selenium.webdriver.common.by import By
from cv2 import imread, QRCodeDetector


def ScanQRCode(path):
    img = imread(path)
    det = QRCodeDetector()
    info, pts, st_code = det.detectAndDecode(img)
    return info


def MatchField(m):
    if m == "姓名":
        return "冯洋一"
    elif m == "班级":
        return "智医2301"
    elif m == "学号":
        return "6401230103"
    else:
        return "啥玩意?"


if __name__ == "__main__":
    cnt = 0
    # url = ScanQRCode(r"10171030.png")
    url = "https://www.wjx.cn/vm/evfoZuA.aspx# "
    browser = selenium.webdriver.Chrome()
    browser.get(url)
    # WebDriverWait(browser, 5).until(lambda d: "" in d.page_source)
    while True:
        ques = browser.find_elements(By.CSS_SELECTOR, '[class="field ui-field-contain"]')
        for que in ques:
            que_type = que.find_element(By.XPATH, '[div2]').get_attribute('class')
            print(que_type)
        try:
            # browser.find_element(By.XPATH, '[class="field.ui-field-contain"]').click()  # 点击提交
            pass
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
