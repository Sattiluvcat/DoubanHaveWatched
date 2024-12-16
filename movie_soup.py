import json
import time

import requests
from bs4 import BeautifulSoup
from pycountry import languages

from utils.extract import director_duration_tags, language
from utils.extract import extract_first_date, actor_actress

movies = []
# 粗暴枚举
tag_list = ["喜剧", "爱情", "动作", "科幻", "动画", "悬疑", "惊悚", "恐怖", "犯罪", "同性", "音乐", "歌舞", "传记","历史", "战争",
            "西部", "奇幻", "冒险","剧情","灾难", "武侠", "情色", "纪录片", "短片", "儿童", "家庭", "古装", "运动", "黑色电影",
            "烂片", "cult","鬼怪", "黑帮", "女性", "荒诞", "史诗", "真实事件改编"]

for i in range(0, 35):

    url = (f'https://movie.douban.com/people/{user_id}/collect?start={i * 15}&sort=time&rating=all&mode=grid&type=all'
           f'&filter=all')
    header = {
        'Authorization': f'Bearer {upload_auth_token}',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0',
    }
    # print(url)
    response = requests.get(url, headers=header)
    print(response.status_code)
    # print(response.text)
    soup = BeautifulSoup(response.text, 'html.parser')

    # 根据F12网页结构逐条获取信息 定位到最近的一个div即可
    for item in soup.select('div.item.comment-item'):
        title = item.select_one('div.info li.title a em').text.strip()
        link = item.select_one('div.info li.title a').get('href')
        span_elements = item.select('div.info li span')
        star_mine_str = None
        for span in span_elements:
            classes = span.get('class')
            for cls in classes:
                if cls.startswith('rating') and cls[6] in '12345':
                    star_mine_str = cls
                    break
            if star_mine_str:
                break
        # 综合信息
        # print(star_mine_str)
        star_mine=''
        # 针对未评分电影的星星处理——置空
        if star_mine_str is not None:
            # print(star_mine_str[0].strip())
            star_mine=star_mine_str[6]
        # print(star_mine)
        comp_load = item.select_one('div.info li.intro').text.strip()
        # print(comp_load)
        release_time = extract_first_date(comp_load)
        actor_actresses = actor_actress(comp_load, 3)
        res_director_duration_tags=director_duration_tags(comp_load, tag_list)
        languages=language(comp_load)
        movies.append({'title': title, 'link': link,'star_mine':star_mine,'release_time':release_time,
                       'actor_actresses':actor_actresses,
                       'director':res_director_duration_tags[0],
                       'duration':res_director_duration_tags[1],
                       'tags':res_director_duration_tags[2],'languages':languages})
    print(i)
    # 等待4s
    # time.sleep(2)

# 保存dat
with open('movies_raw.dat', 'w', encoding='utf-8') as f:
    for movie in movies:
        json.dump(movie, f, ensure_ascii=False)
        f.write('\n')
