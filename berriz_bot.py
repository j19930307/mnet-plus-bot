import json
import random
import time

import requests
from fake_useragent import UserAgent

from firebase import Firebase
from sns_type import SnsType
from datetime import datetime, timezone


class BerrizBot:
    def __init__(self, firebase: Firebase):
        self.__firestore = firebase

    def execute(self):
        for doc in self.__firestore.get_subscribed_list(SnsType.BERRIZ):
            # 每隔 3 ~ 5 秒執行
            random_sleep_time = random.uniform(3, 5)
            time.sleep(random_sleep_time)

            community_id = doc.get("community_id")
            board_id = doc.get("board_id")
            discord_channel_id = doc.get("discord_channel_id")
            # 取得上次最新發文時間
            last_updated = doc.get("updated_at")
            print(f"上次發文時間: {last_updated}")
            print("開始抓取資料...")
            posts = self._extract_posts_data(community_id=community_id, board_id=board_id, last_updated=last_updated)
            if posts:



    def _extract_posts_data(self, community_id: str, board_id: str, last_updated: datetime):
        url = f"https://svc-api.berriz.in/service/v1/community/{community_id}/boards/{board_id}/feed?pageSize=10"
        ua = UserAgent()
        user_agent = ua.random
        headers = {'user-agent': user_agent}
        response = requests.get(url=url, headers=headers)
        data = json.loads(response.text)

        posts_data = []
        # 取得所有貼文內容
        contents = data['data']['contents']

        for content in contents:
            post = content['post']
            writer = content['writer']
            created_at = datetime.strptime(post['createdAt'], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
            if created_at < last_updated:
                continue
            # 提取所需字段
            post_info = {
                'body': post['body'],
                'createdAt': post['createdAt'],
                'writer_name': writer['name'],
                'writer_imageUrl': writer['imageUrl'],
                'photo_urls': []
            }

            # 提取所有照片的URL
            if 'media' in post and 'photo' in post['media']:
                for photo in post['media']['photo']:
                    post_info['photo_urls'].append(photo['imageUrl'])

            posts_data.append(post_info)

        return posts_data
