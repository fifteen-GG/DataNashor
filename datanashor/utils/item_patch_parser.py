import json
import requests
from bs4 import BeautifulSoup


def patch_version_parser():
    url = 'https://developer.riotgames.com/docs/lol#data-dragon_data-assets'
    response = requests.get(url)

    if response.status_code == 200:
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')
        version = soup.select_one(
            'body > div.container > div.layout > div.content-container > div.content > p:nth-child(69) > code:nth-child(1)')
    else:
        raise Exception('서버 접속 불가')

    return version.get_text()


def item_patch_parser(dest_dir):
    try:
        patch_num = patch_version_parser()
    except:
        print('버전 파싱 에러')
        return

    url = requests.get(
        f'https://ddragon.leagueoflegends.com/cdn/{patch_num}/data/ko_KR/item.json')
    text = url.text
    src = json.loads(text)
    item_dict = dict()
    data = src['data']

    for item_id in data.keys():
        item_dict[item_id] = {'name': data[item_id]
                              ['name'], 'gold': data[item_id]['gold']['total']}

    with open(dest_dir, 'w', encoding='UTF-8') as dest:
        json.dump(item_dict, dest, ensure_ascii=False)
