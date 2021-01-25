import xlrd
import requests
import json
import re

from retrying import retry

commenturl = 'https://comment.sina.com.cn/page/info?version=1&format=json&channel=gn&newsid=comos-{}&group=0&compress=0&ie=utf-8&oe=utf-8&page=1&page_size=3&t_size=3&h_size=3&thread=1&uid=unlogin_user&'
output = []

def get_comments():
    wb = xlrd.open_workbook('sinanews2.xls')
    sh = wb.sheet_by_name('Sheet1')
    for i in range(1,sh.nrows):
        url = sh.cell(i,1).value
        print(url)
        article = {'url': sh.cell(i, 1).value, 'title': sh.cell(i, 2).value, 'date': sh.cell(i, 3).value,
                   'source': sh.cell(i, 4).value, 'content': sh.cell(i, 5).value}
        m = re.search('doc-i(.*).shtml',url)
        newsid = m.group(1)
        try:
            article['comments'] = get_json(newsid)
        except KeyError:
            article['comments'] = []
        output.append(article)


@retry(stop_max_attempt_number=20)
def get_json(newsid):
    comos = []
    comments = requests.get(commenturl.format(newsid))
    comments.encoding = ('utf-8')
    jd = json.loads(comments.text)
    for x in range(0, min(3, jd['result']['count']['thread_show'])):
        comos.append(jd['result']['hot_list'][x]['content'])
    return comos

if __name__ == '__main__':
    get_comments()

    with open('sina_news2.json','w',encoding='utf-8') as file_obj:
        json.dump(output,file_obj,sort_keys=True, indent=4, ensure_ascii=False)

