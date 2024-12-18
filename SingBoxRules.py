# -*- coding: utf-8 -*-

base_url = "https://testingcf.jsdelivr.net/gh/MetaCubeX/meta-rules-dat@sing/geo-lite/"
rulesets = {
    "private":{\
        "geosite":[
            "private",
            "cn",
            "bilibili"
        ],
        "geoip":[
            "private",
            "cn",
            "bilibili"
        ]
    },
    "proxy":{
        "geosite":[
            "proxy",
            "proxymedia",
            "apple",
            "applemusic",
            "biliintl",
            "cloudflare",
            "ehentai",
            "github",
            "google",
            "microsoft",
            "netflix",
            "openai",
            "pixiv",
            "telegram",
            "twitter",
            "youtube"
        ],
        "geoip":[
            "apple",
            "cloudflare",
            "cloudfront",
            "facebook",
            "google",
            "jp",
            "netflix",
            "telegram",
            "twitter"
        ]
    }
}

import json
import requests
import threading
import traceback


def get_online_json(url, max_retry_times=5):
    print('try to get online json')
    print('url:"{}"\nmax retry times:{}'.format(url, max_retry_times))
    retry_times = 1
    while (retry_times < max_retry_times + 1):
        try:
            print('try times:{}'.format(retry_times))
            stringContent = str(requests.get(url).content, 'utf-8')
            if stringContent is not None and stringContent != '':
                online_json = json.loads(stringContent)
                retry_times = max_retry_times + 2
        except:
            retry_times = retry_times + 1
    print('get online json successful: {}\n'.format(url))
    return online_json


def merge_json():
    print('try to merge json')
    rules = dict()
    rules["version"] = 1
    rules["rules"] = []
    rules["rules"].append(dict())
    sum = 0
    for proxy_type in rulesets:
        for rule_type in rulesets[proxy_type]:
            sum = sum + len(rulesets[proxy_type][rule_type])
    num = 0
    for proxy_type in rulesets:
        if proxy_type not in rules["rules"][0]:
            rules["rules"][0] = dict()
        for rule_type in rulesets[proxy_type]:
            for remote_rule in rulesets[proxy_type][rule_type]:
                url = base_url + rule_type + "/" + remote_rule + ".json"
                rule_json = get_online_json(url)
                rule_json = rule_json["rules"]
                for rule in rule_json:
                    for r in rule:
                        if not isinstance(rule[r], list):
                            continue
                        if r not in rules["rules"][0]:
                            rules["rules"][0][r] = set()
                        rules["rules"][0][r] = rules["rules"][0][r] | set(rule[r])
                    num = num + 1
                    print("progress: {}/{} | {}:{}\n".format(num, sum, proxy_type, rule_type))
        for r in rules["rules"][0]:
            rules["rules"][0][r] = sorted(list(rules["rules"][0][r]))
        with open(proxy_type + ".json", 'w', encoding='utf-8') as local_file:
            json_str = json.dumps(rules, ensure_ascii=False, indent=4, separators=(',', ':'))
            print('try to write local file')
            local_file.write(json_str)
            print('write local file successful')


def git_update_workflows(workflows_path):
    with open(workflows_path, "r", encoding="utf-8") as f:
        workflows = f.read()
    import random
    import re
    import time
    m = random.randint(0, 59)
    h = random.randint(0, 8)
    cron = "cron: '{} {} * * *'".format(m, h)
    workflows = re.sub(r"cron: '\d+ \d+ \* \* \*'", cron, workflows)
    timestamp = time.strftime("%Y/%m/%d %H:%M:%S %Z", time.localtime())
    workflows = re.sub(r"# timestamp: .*", "# timestamp: {}".format(timestamp), workflows)
    with open(workflows_path, "w", encoding="utf-8") as f:
        f.write(workflows)


if __name__ == '__main__':
    try:
        t = threading.Thread(target=merge_json)
        t.daemon = True
        t.start()
        t.join(timeout=300)
    except:
        print(traceback.format_exc())
    git_update_workflows(".github/workflows/workflow.yml")
