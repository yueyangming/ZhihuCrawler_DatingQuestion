# coding:utf-8
# Powered By Harold Yue
# Original code fork from https://github.com/maritree/zhihu_spouse
import re
import time
import pandas as pd

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


def get_soup(driver, url,
             wait_time=1.1
             ):
    '''
    Get BeautifulSoup Instance for further extraction.
    '''
    driver.get(url)
    cont = (By.CLASS_NAME, "RichContent-inner")
    WebDriverWait(driver, 30, 0.5).until(EC.presence_of_element_located(cont))
    time.sleep(wait_time)
    str_con = driver.page_source.encode('utf-8')
    soup = BeautifulSoup(str_con, 'lxml')
    return soup


def extract_result_list(soup,
                        city_keyword='上海',
                        gender_keyword='女',
                        text_len_filter=500
                        ):
    '''
    从Soup Instance中提取结果
    :param city_keyword: String
    :param gender_keyword: String
    :param text_len_filter: Integer, Default is 500
    :return: List
    '''
    question_string = soup.text.split('\n')[0]

    items = soup.find(class_='Question-main').find_all(class_='List-item')
    result_list = []
    for item in items:
        # name_val = item.find(class_='ContentItem AnswerItem').attrs['name']  #
        text_val = re.sub(r'<.*?>', ' ', item.find(class_='RichText ztext CopyrightRichText-richText').text)
        text_val = re.sub(r'\s+', ' ', text_val)
        text_val = text_val.strip()
        re.sub('<.*?>', '', text_val)

        answer_url = item.contents[0].contents[3].attrs['content']
        if gender_keyword in text_val and len(text_val) > text_len_filter:  # 满足性别要求以及字数
            if city_keyword in question_string:  # City specification in the Question.
                print(len(text_val), answer_url, text_val)
                result_list.append([len(text_val), answer_url, text_val])

            elif city_keyword in text_val:
                print(len(text_val), answer_url, text_val)
                result_list.append([len(text_val), answer_url, text_val])
    return result_list


def _main(url_list, start, end, city_keyword, gender_keyword, text_len_filter,
          debug=False):
    option = webdriver.ChromeOptions()
    option.add_argument("headless")
    boswer = webdriver.Chrome(r'driver\chromedriver.exe', chrome_options=option)
    all_result = []
    for url_index, url in enumerate(url_list):
        for page_count in range(start, end):  # 这里要改成当前按照时间排序的总页数量+1,或者设置的大一点也可以。超出实际页码后手动退出程序即可
            current_url = url % page_count
            try:
                soup = get_soup(boswer, current_url, wait_time=1.1)
                temp_result_list = extract_result_list(soup,
                                                       city_keyword=city_keyword,
                                                       gender_keyword=gender_keyword,
                                                       text_len_filter=text_len_filter)
                print('第%d页爬取完成' % page_count)
            except Exception as e:
                if debug:
                    print('第一次失败')
                    print(e)
                break
            all_result += temp_result_list

    df = pd.DataFrame(all_result)
    DateString = time.strftime('%Y-%m-%d', time.localtime())
    df.to_excel('{}_{}_{}_{}-{}.xlsx'.format(city_keyword, gender_keyword, DateString, start, end))
    boswer.close()


if __name__ == '__main__':
    # 问题列表。请自行替换成自己感兴趣的问题。
    url_list = ['https://www.zhihu.com/question/275359100/answers/created?page=%d',
                'https://www.zhihu.com/question/308798869/answers/created?page=%d',
                'https://www.zhihu.com/question/364035162/answer/created?page=%d',
                'https://www.zhihu.com/question/356957129/answer/created?page=%d']
    gender_keyword = '女'  # 性别
    city_keyword = '上海'  # 城市
    text_len_filter = 500  # 最低字数限制
    start = 1  # 开始页码
    end = 20  # 结束页码

    _main(url_list, start, end, city_keyword, gender_keyword, text_len_filter)
