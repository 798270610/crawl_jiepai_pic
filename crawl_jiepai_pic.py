"""
    缺少验证码识别
"""
import requests
from urllib.parse import urlencode
import os
from hashlib import md5
from multiprocessing.pool import Pool
from requests import codes


headers = {
    'authority': 'www.toutiao.com',
    'method': 'GET',
    'path': '/api/search/content/?aid=24&app_name=web_search&offset=100&format=json&keyword=%E8%A1%97%E6%8B%8D&autoload=true&count=20&en_qc=1&cur_tab=1&from=search_tab&pd=synthesis&timestamp=1556892118295',
    'scheme': 'https',
    'accept': 'application/json, text/javascript',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'zh-CN,zh;q=0.9',
    'content-type': 'application/x-www-form-urlencoded',
    'cookie': 'tt_webid=6686738543769060877; WEATHER_CITY=%E5%8C%97%E4%BA%AC; UM_distinctid=16a7d235d9041f-0e169f5e22e7b5-39395704-1fa400-16a7d235d9174e; tt_webid=6686738543769060877; csrftoken=dd5f783688e4d7cbdad02d2c327bdf7a; CNZZDATA1259612802=1082695115-1556872462-%7C1556883262; s_v_web_id=c24ad746965be967215f64165e913d08',
    'referer': 'https://www.toutiao.com/search/?keyword=%E8%A1%97%E6%8B%8D',
    'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36',
    'x-requested-with': 'XMLHttpRequest',
}


def get_page(offest, keyword):
    params = {
        'aid': '24',
        'app_name': 'web_search',
        'offset': offest,
        'format': 'json',
        'keyword': keyword,
        'autoload': 'true',
        'count': '20',
        'en_qc': '1',
        'cur_tab': '1',
        'from': 'search_tab',
        'pd': 'synthesis',
    }
    url = 'https://www.toutiao.com/api/search/content/?'+urlencode(params)
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
    except requests.ConnectionError:
        print('索引出错')
        return None


def get_images(json):
    if json.get('data'):
        data = json.get('data')
        for item in data:
            if item.get('cell_type') is not None:
                continue
            title = item.get('title')
            images = item.get('image_list')
            for image in images:
                yield {
                    'image': image.get('url'),
                    'title': title
                }


def save_image(item):
    img_path = 'jiepai' + os.path.sep + item.get('title').replace('|', '')
    if not os.path.exists(img_path):
        os.makedirs(img_path)
    try:
        response = requests.get(item.get('image'))
        if codes.ok == response.status_code:
            file_path = img_path+'/{0}.{1}'.format(md5(response.content).hexdigest(), 'jpg')
            if not os.path.exists(file_path):
                with open(file_path, 'wb') as f:
                    f.write(response.content)
                print('Downloaded image path is %s' % file_path)
            else:
                print('Already Downloaded', file_path)
    except requests.ConnectionError:
        print('Failed to Save Image，item %s' % item)


def main(offest):
    json = get_page(offest, '街拍')
    for item in get_images(json):
        print(item)
        save_image(item)


GROUP_START = 0
GROUP_END = 5


if __name__ == '__main__':
    pool = Pool()
    groups = ([x * 20 for x in range(GROUP_START, GROUP_END + 1)])
    pool.map(main, groups)
    pool.close()
    pool.join()
