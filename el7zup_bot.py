import json
import os
import requests
from dateutil import parser
from fake_useragent import UserAgent
from discord_bot import DiscordBot
from firebase import Firebase
from sns_info import SnsInfo, Profile
from sns_type import SnsType

ua = UserAgent()
user_agent = ua.random
headers = {'user-agent': user_agent}


def convert_to_datetime(date_string):
    return parser.isoparse(date_string)


class EL7ZUPBot:
    def __init__(self, firebase: Firebase):
        self.__firestore = firebase
        self.__discord_bot = DiscordBot(webhook_url=os.environ["EL7ZUP_WEBHOOK"])

    def execute(self):
        # 取得上次最新發文時間
        last_updated = self.__firestore.get_updated_at(SnsType.BSTAGE, "EL7Z UP")
        print(f"上次發文時間: {last_updated}")
        print("開始抓取資料...")
        request = requests.get(headers=headers,
                               url="https://artist.mnetplus.world/svc/stg/el7zup/home/api/v1/home/star?page=1&pageSize=10")
        data = json.loads(request.text)

        sns_info_list = []
        for item in data["feeds"]["items"]:
            published_at_datetime = convert_to_datetime(item["publishedAt"])
            if last_updated < published_at_datetime:
                sns_info = SnsInfo(
                    post_link=f"https://artist.mnetplus.world/main/stg/el7zup/story/feed/{item['typeId']}",
                    profile=Profile(item["author"]["nickname"], item["author"]["avatarImgPath"]),
                    content=item["description"], images=[image for image in item.get("images", [])],
                    timestamp=published_at_datetime)
                sns_info_list.append(sns_info)

        post_count = len(sns_info_list)
        if post_count != 0:
            print(f"有 {post_count} 則發文")
            for sns_info in reversed(sns_info_list):
                pass
                self.__discord_bot.send_message(sns_info=sns_info)
            # 儲存最新發文時間
            updated_at = max([sns_info.timestamp for sns_info in sns_info_list])
            print(f"更新最後發文時間: {updated_at}")
            self.__firestore.set_updated_at(SnsType.BSTAGE, "EL7Z UP", updated_at)
        else:
            print("無新發文")
        print("抓取結束")
