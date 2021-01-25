import pandas
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from selenium import webdriver


def get_news_content(url, soup):
    result = {}
    if (len(soup.select('.second-title')) > 0) and (len(soup.select('.date')) > 0) and (len(soup.select('.source'))>0):
        result = {'url': url, 'title': soup.select('.second-title')[0].text, 'date': soup.select('.date')[0].text,
                  'source': soup.select('.source')[0].text}
        article = []
        for v in soup.select('.article p')[:-1]:
            article.append(v.text.strip())
        result['content'] = '\n'.join(article)
    return result


def get_page_news():
    news = browser.find_elements_by_xpath('//div[@class="d_list_txt"]/ul/li/span/a')
    page_news = []
    for i in news:
        link = i.get_attribute('href')
        res = requests.get(link)
        res.encoding = 'utf-8'
        soup = BeautifulSoup(res.text, 'html.parser')
        if len(soup.select('.second-title')) > 0:
            string = soup.select('.second-title')[0].text
        if '疫' in string or '肺炎' in string or '病毒' in string:
            page_news.append(get_news_content(link, soup))
    return page_news


def get_data():
    url = 'https://news.sina.com.cn/roll/#pageid=153&lid=2510&etime={}&stime={}&ctime={}&date={}&k=&num=50&page=1'
    startEtime = 1575734400 + 86400 * 112
    startSCtime = 1575820800 + 86400 * 112


    info = []
    # 190days
    for i in range(0, 80):
        browser.refresh()
        newsurl = url.format(startEtime, startSCtime, startSCtime, datetime.fromtimestamp(startEtime).date())
        browser.get(newsurl)
        info.extend(get_page_news())
        startEtime = startEtime + 86400
        startSCtime = startSCtime + 86400
    return info


if __name__ == '__main__':
    browser = webdriver.Ie()
    browser.get('http://www.baidu.com')
    browser.implicitly_wait(10)
    new_info = get_data()
    df = pandas.DataFrame(new_info)
    df.to_excel('sinanews2.xlsx')
