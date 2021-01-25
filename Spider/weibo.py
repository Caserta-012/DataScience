import requests
import json
import re
from retrying import retry

base_url = 'https://weibo.cn/1784473157/profile?hasori=0&haspic=0&starttime=20200606&endtime=20200615&advancedfilter=1&page={}'
headers = {
    'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36 Edg/88.0.705.50',
    'Host': 'weibo.cn',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Cookie': '_T_WM=4beffdd16b7262a800dca0e6b2c267d6; SCF=AgcK8lbljS_WQmUVjoXL_FQNEdTHHl8zFmiMez0zWV6-klyOS-FC6Dm3BcF9jvj1-HBquEicrQ588xKMTtZ_VMk.; SUB=_2A25NCinrDeRhGeBO71IR9SbPwzuIHXVu9LejrDV6PUJbkdAKLUH-kW1NSh7RMBy6JTjwM8ng8jnemA_GfSFLsZbc; SSOLoginState=1611553211',
    'DNT': '1',
    'Connection': 'keep-alive'
}
comment_url = 'https://weibo.cn/comment/{}?uid=1784473157&rl=1#cmtfrm'


def get_title(news):
    pattern = re.compile('【.*?】')
    try:
        title = re.findall(pattern, news)[0].lstrip('【').rstrip('】')
    except IndexError:
        return ""
    return remove_links(title)


def get_news_info(title, news):
    article = {'title': title}
    pattern = re.compile('】.*?</span>')
    content = re.findall(pattern, news)[0].lstrip('】')
    article['content'] = remove_links(content)
    pattern = re.compile("赞\[.*?]")
    article['总点赞'] = re.findall(pattern, news)[0].lstrip('赞[').rstrip(']')
    pattern = re.compile("评论\[.*?]")
    article['总评论'] = re.findall(pattern, news)[0].lstrip('评论[').rstrip(']')
    pattern = re.compile('<span class="ct">.*?</span>')
    article['date'] = re.findall(pattern, news)[0].lstrip('<span class="ct">')[0:10]
    print(article['date'])
    pattern = re.compile('attitude/.*?/')
    newsid = re.findall(pattern, news)[0].lstrip('attitude/').rstrip('/')
    try:
        article['comments'] = get_comments(newsid)
    except requests.exceptions.SSLError:
        article['comments'] = []
    return article


@retry(stop_max_attempt_number=5, wait_fixed=2000)
def get_comments(newsid):
    comments = []
    html = requests.get(comment_url.format(newsid))
    pattern = re.compile('<div class="c" id="C_.*?</div>')
    comment_block = re.findall(pattern, html.text)
    pattern = re.compile('<span class="ctt">.*?</span>')
    for i in range(min(len(comment_block), 10)):
        tmp = remove_links(re.findall(pattern, comment_block[i])[0])
        if '回复' in tmp:
            tmp = tmp[tmp.find(':') + 1:]
        if len(tmp) == 0:
            continue
        comments.append(tmp)
    return comments


def remove_links(string):
    pattern = re.compile('<.*?>')
    string = re.sub(pattern, '', string)
    pattern = re.compile('http.*?$')
    string = re.sub(pattern, '', string)
    string = string.replace('#', '')
    return string


@retry(stop_max_attempt_number=5, wait_fixed=2000)
def get_page_news(newsurl):
    data = []
    response = requests.get(newsurl, headers=headers)
    pattern = re.compile('<span class="ctt">.*?<span class="ct">.*?</span>', re.S)
    items = re.findall(pattern, response.text)
    for i in items:
        if '【' in i:
            title = get_title(i)
            if '疫' in title or '肺炎' in title or '病毒' in title or '新冠' in title:
                data.append(get_news_info(title, i))
    return data


def get_data():
    info = []
    for i in range(1, 68):
        newsurl = base_url.format(i)
        try:
            info.extend(get_page_news(newsurl))
        except requests.exceptions.SSLError:
            continue
    return info


if __name__ == '__main__':
    with open('data/chinanews.json', 'w', encoding='utf-8') as file_obj:
        json.dump(get_data(), file_obj, sort_keys=True, indent=4, ensure_ascii=False)
