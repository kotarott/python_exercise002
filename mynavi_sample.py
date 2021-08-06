import os
from numpy import NaN
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options
import time
import pandas as pd
import datetime
from webdriver_manager.chrome import ChromeDriverManager

# ドライバ更新関数
def setup_class():
    Chrome(ChromeDriverManager().install())

# Chromeを起動する関数
def set_driver(driver_path, headless_flg):

    # ドライバの更新
    setup_class()

    if "chrome" in driver_path:
        options = ChromeOptions()
    else:
        options = Options()

    # ヘッドレスモード（画面非表示モード）をの設定
    if headless_flg == True:
        options.add_argument('--headless')

    # 起動オプションの設定
    options.add_argument(
        '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36')
    # options.add_argument('log-level=3')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-ssl-errors')
    options.add_argument('--incognito')          # シークレットモードの設定を付与

    # ChromeのWebDriverオブジェクトを作成する。
    if "chrome" in driver_path:
        return Chrome(executable_path=os.getcwd() + "/" + driver_path,options=options)
    else:
        return Firefox(executable_path=os.getcwd()  + "/" + driver_path,options=options)

# main処理
def main(loop_count=1, search_keyword="高収入"):

    makeLog('スクレイピングを開始します。')

    # driverを起動
    if os.name == 'nt': #Windows
        driver = set_driver("chromedriver.exe", False)
    elif os.name == 'posix': #Mac
        driver = set_driver("chromedriver", False)

    makeLog('ドライバを起動しました。')

    # 直接キーワードの検索結果のページを開く
    driver.get("https://tenshoku.mynavi.jp/list/kw" + search_keyword)

    # # Webサイトを開く
    # driver.get("https://tenshoku.mynavi.jp/")
    # time.sleep(5)
    # # ポップアップを閉じる
    # driver.execute_script('document.querySelector(".karte-close").click()')
    # time.sleep(5)
    # # ポップアップを閉じる
    # driver.execute_script('document.querySelector(".karte-close").click()')

    # # 検索窓に入力
    # driver.find_element_by_class_name("topSearch__text").send_keys(search_keyword)
    # # 検索ボタンクリック
    # driver.find_element_by_class_name("topSearch__button").click()

    makeLog('検索しました。')

    time.sleep(5)
    try:
        while driver.find_element_by_class_name("karte-close") != "":
            driver.execute_script('document.querySelector(".karte-close").click()')
    except:
        pass

    # 空のDataFrame作成
    df = pd.DataFrame()

    for i in range(loop_count):

        # ページ終了まで繰り返し取得
        # 検索結果の一番上の会社名を取得
        name_list = driver.find_elements_by_class_name("cassetteRecruit__name")
        applicant_list =driver.find_elements_by_xpath("/html/body/div[1]/div[3]/form/div/div/div/div[2]/div[1]/table/tbody/tr[2]/td")
        income_list = driver.find_elements_by_xpath("/html/body/div[1]/div[3]/form/div/div/div/div[2]/div[1]/table/tbody/tr[5]/td")

        makeLog(f'{i+1}ページ内のデータを取得しています。')
        
        # 1ページ分繰り返し
        # print(len(name_list))
        for count, (name, applicant, income) in enumerate(zip(name_list, applicant_list, income_list)):
            # print(name.text, applicant.text, income.text)
            # DataFrameに対して辞書形式でデータを追加する
            makeLog(f'{count}件目のデータを取得しています。')
            df = df.append(
                {"会社名": name.text, 
                "対象": applicant.text,
                "初年度年収": income.text}, 
                ignore_index=True)

        driver.execute_script('document.querySelector(".iconFont--arrowLeft").click()')
        time.sleep(2)

        makeLog('画面遷移しました。')

    makeLog('処理を終了します。')
    return df

# 会社名のみを取得する関数
def splitItems(items, symbol):
    item_list = {}

    for item in items:
        first_second = item.split(symbol)

        if (len(first_second) >= 2):
            item_list[first_second[0]] = first_second[1]
        else:
            item_list[first_second[0]] = NaN

    return item_list

# CSV作成関数
def createCSV(data, file_name="company_list.csv"):
    num = 0
    while num == 0:
        if os.path.exists(file_name):
            print(f"ファイル名{file_name}は存在します。")
            num = 0
            file_name = input("ファイル名を入力してください >>>")
            file_name += ".csv"
        else:
            data.to_csv(file_name)
            makeLog(f'ファイル名:{file_name} を作成しました。')
            return print("ファイルを作成しました。")

# ログ作成関数
def makeLog(comment):
    path = "log.csv"
    now = datetime.datetime.now()
    time_stamp = now.strftime("%Y/%m/%d %H:%M:%S")
    logs = ','.join([time_stamp, comment])

    if not os.path.exists(path):
        with open(path, 'w', encoding='utf-8') as f:
            f.write(logs)
    else:
        with open(path, 'a', encoding='utf-8') as f:
            f.write('\n' + logs)



# 1.会社名の取得
# company_list = main()
# print(splitItems(list(company_list["会社名"]), ' | ').keys())

# 2.その他要素の取得
# company_list = main()
# print(list(company_list["対象"]))

# 3.2ページ目以降も
# company_list = main(2)
# print(splitItems(list(company_list["会社名"]), ' | ').keys())

# 4.コンソールからキーワード指定
# word = input("検索ワードを入れてください >>>")
# company_list = main(1, word)
# print(splitItems(list(company_list["会社名"]), ' | ').keys())

# 5.CSVに保存
# company_list = main()
# createCSV(company_list)

# 6.エラースキップ
# try:
#     company_list = main(1, "リモート")
#     createCSV(company_list)
# except:
#     print("正しく処理されませんでした。")

# 7.logファイル付き
company_list = main(1, "リモート")
createCSV(company_list)

# 直接起動された場合はmain()を起動(モジュールとして呼び出された場合は起動しないようにするため)
if __name__ == "__main__":
    # main()
    pass