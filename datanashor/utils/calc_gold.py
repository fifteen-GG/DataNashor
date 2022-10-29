import json
from datanashor.utils.item_patch_parser import item_patch_parser


def calc_gold(replay_data_dir, item_data_dir):
    with open(replay_data_dir, encoding='UTF-8') as src:
        source = json.load(src)
    try:
        with open(item_data_dir, encoding='UTF-8') as src:
            item_dict = json.load(src)
    except FileNotFoundError:
        item_patch_parser(item_data_dir)
        with open(item_data_dir, encoding='UTF-8') as src:
            item_dict = json.load(src)

    gold = 0
    count = 0

    for data in source:
        for user in data['player_data']:
            gold = 0
            count = 1
            for item in user['items']:
                count = item['count']
                gold += (item_dict[str(item['itemID'])]['gold']) * count
            user['gold'] = gold

    with open(replay_data_dir, 'w', encoding='UTF-8') as src:
        json.dump(source, src, ensure_ascii=False)
