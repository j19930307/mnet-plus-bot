import json
import os
import random
import time

import discord
import requests
from dateutil import parser
from fake_useragent import UserAgent

import discord_bot
import m3u8
from firebase import Firebase
from sns_info import SnsInfo, Profile
from sns_type import SnsType

ua = UserAgent()
user_agent = ua.random
headers = {'user-agent': user_agent}


def convert_to_datetime(date_string):
    return parser.isoparse(date_string)


class BstageBot:
    def __init__(self, firestore: Firebase):
        self.__firestore = firestore

    def execute(self):
        for doc in self.__firestore.get_subscribed_list(SnsType.BSTAGE):
            # 每隔 3 ~ 5 秒執行
            random_sleep_time = random.uniform(3, 5)
            time.sleep(random_sleep_time)
            artist = doc.id
            discord_channel_id = doc.get("discord_channel_id")
            # 取得上次最新發文時間
            last_updated = doc.get("updated_at")
            print(f"上次發文時間: {last_updated}")
            print("開始抓取資料...")
            request = requests.get(headers=headers,
                                   url=f"https://{artist}.bstage.in/svc/home/api/v1/home/star?page=1&pageSize=10")
            data = json.loads(request.text)

            sns_info_list = []
            for item in data["feeds"]["items"]:
                # 跳過付費文章
                if item["type"] == "FEED_ITEM_STAR_POST_PAID":
                    continue
                published_at_datetime = convert_to_datetime(item["publishedAt"])
                if last_updated < published_at_datetime:
                    images = []
                    videos = []
                    if item.get("images") is not None:
                        images += [image for image in item.get("images")]
                    if item.get("video") is not None:
                        images += [
                            f"https://image.static.bstage.in/cdn-cgi/image/metadata=none/{artist}" + thumbnail["path"]
                            for thumbnail in item["video"]["thumbnailPaths"]]
                        videos.append(f"https://media.static.bstage.in/{artist}" + item["video"]["hlsPath"]["path"])
                    sns_info = SnsInfo(
                        post_link=f"https://{artist}.bstage.in/story/feed/{item['typeId']}",
                        profile=Profile(item["author"]["nickname"], item["author"]["avatarImgPath"]),
                        content=item["description"], images=images, videos=videos,
                        timestamp=published_at_datetime)
                    print(sns_info)
                    sns_info_list.append(sns_info)
                else:
                    break

            post_count = len(sns_info_list)
            if post_count != 0:
                print(f"有 {post_count} 則發文")
                for sns_info in reversed(sns_info_list):
                    discord_bot.send_message_by_api(
                        discord_channel_id=discord_channel_id, content=sns_info.post_link,
                        embeds=discord_bot.generate_embeds(sns_info))
                    videos = sns_info.videos
                    if videos is not None and len(videos) > 0:
                        file_paths = []
                        for video in videos:
                            file_path = m3u8.download_m3u8_to_mp4(video, f"{time.time()}.mp4")
                            file_paths.append(file_path)

                        # 直接傳入檔案路徑列表
                        discord_bot.send_message_by_api(
                            discord_channel_id=discord_channel_id,
                            content="",
                            files=file_paths  # 直接傳入路徑列表
                        )

                        # 清理暫存檔案
                        for file_path in file_paths:
                            if os.path.exists(file_path):
                                os.remove(file_path)
                # 儲存最新發文時間
                updated_at = max([sns_info.timestamp for sns_info in sns_info_list])
                print(f"更新最後發文時間: {updated_at}")
                self.__firestore.set_updated_at(SnsType.BSTAGE, artist, updated_at)
            else:
                print("無新發文")
            print("抓取結束")

        for doc in self.__firestore.get_subscribed_list(SnsType.MNET_PLUS):
            # 每隔 3 ~ 5 秒執行
            random_sleep_time = random.uniform(3, 5)
            time.sleep(random_sleep_time)
            artist = doc.id
            discord_channel_id = doc.get("discord_channel_id")
            # 取得上次最新發文時間
            last_updated = doc.get("updated_at")
            print(f"上次發文時間: {last_updated}")
            print("開始抓取資料...")
            request = requests.get(headers=headers,
                                   url=f"https://artist.mnetplus.world/svc/stg/{artist}/home/api/v1/home/star/feeds")
            data = json.loads(request.text)

            sns_info_list = []
            for item in data["items"]:
                # 跳過付費文章
                if item["type"] == "FEED_ITEM_STAR_POST_PAID":
                    continue
                published_at_datetime = convert_to_datetime(item["publishedAt"])
                if last_updated < published_at_datetime:
                    images = []
                    videos = []
                    if item.get("images") is not None:
                        images += [image for image in item.get("images")]
                    if item.get("video") is not None:
                        artist_name = 'limelight' if artist == 'madein' else artist
                        images += [
                            f"https://image.static.bstage.in/cdn-cgi/image/metadata=none/{artist_name}" +
                            thumbnail["path"]
                            for thumbnail in item["video"]["thumbnailPaths"]
                        ]
                        videos.append(
                            f"https://media.static.bstage.in/{artist_name}" + item["video"]["hlsPath"]["path"]
                        )
                    sns_info = SnsInfo(
                        post_link=f"https://artist.mnetplus.world/main/stg/{artist}/story/feed/{item['typeId']}",
                        profile=Profile(item["author"]["nickname"], item["author"]["avatarImgPath"]),
                        content=item["description"], images=images, videos=videos,
                        timestamp=published_at_datetime)
                    print(sns_info)
                    sns_info_list.append(sns_info)
                else:
                    break

            post_count = len(sns_info_list)
            if post_count != 0:
                print(f"有 {post_count} 則發文")
                for sns_info in reversed(sns_info_list):
                    discord_bot.send_message_by_api(
                        discord_channel_id=discord_channel_id,
                        content=sns_info.post_link,
                        embeds=discord_bot.generate_embeds(sns_info)
                    )

                    videos = sns_info.videos
                    if videos is not None and len(videos) > 0:
                        file_paths = []
                        for video in videos:
                            file_path = m3u8.download_m3u8_to_mp4(video, f"{time.time()}.mp4")
                            file_paths.append(file_path)

                        # 直接傳入檔案路徑列表
                        discord_bot.send_message_by_api(
                            discord_channel_id=discord_channel_id,
                            content="",
                            files=file_paths  # 直接傳入路徑列表
                        )

                        # 清理暫存檔案
                        for file_path in file_paths:
                            if os.path.exists(file_path):
                                os.remove(file_path)
                # 儲存最新發文時間
                updated_at = max([sns_info.timestamp for sns_info in sns_info_list])
                print(f"更新最後發文時間: {updated_at}")
                self.__firestore.set_updated_at(SnsType.MNET_PLUS, artist, updated_at)
            else:
                print("無新發文")
            print("抓取結束")


if __name__ == '__main__':
    file_paths = []
    file_path = m3u8.download_m3u8_to_mp4(
        "https://media.static.bstage.in/limelight/media/68c166446b9b4960d49eac08/hls/ori.m3u8", f"{time.time()}.mp4")
    file_paths.append(file_path)
