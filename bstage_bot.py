import json
import os
import random
import time

from sns_core.clients.discord_messages import post_message, build_embeds
from sns_core.utils.media import download_video_to_local, cleanup_local_files, download_m3u8_to_mp4

import requests
from dateutil import parser
from fake_useragent import UserAgent
from sns_core import (
    FirestoreSubscriptionStore,
    PostAuthor,
    SocialPlatform,
    SocialPost,
)

ua = UserAgent()
user_agent = ua.random
headers = {'user-agent': user_agent}


def convert_to_datetime(date_string):
    return parser.isoparse(date_string)


class BstageBot:
    def __init__(self, firestore: FirestoreSubscriptionStore):
        self.__firestore = firestore

    async def execute(self):
        bstage_subscribed_list = await self.__firestore.get_subscribed_list(SocialPlatform.BSTAGE)
        for doc in bstage_subscribed_list:
            # 每隔 3 ~ 5 秒執行
            random_sleep_time = random.uniform(3, 5)
            time.sleep(random_sleep_time)
            artist = doc.id
            discord_channel_id = doc.get("discord_channel_id")
            # 取得上次最新發文時間
            last_updated = doc.get("updated_at")
            print(f"{artist} 上次發文時間: {last_updated}")
            print("開始抓取資料...")
            request = requests.get(headers=headers,
                                   url=f"https://{artist}.bstage.in/svc/home/api/v1/home/star?page=1&pageSize=10")
            data = json.loads(request.text)

            social_posts = []
            for item in data["feeds"]["items"]:
                # 跳過付費文章
                if item["type"] == "FEED_ITEM_STAR_POST_PAID":
                    continue
                published_at_datetime = convert_to_datetime(item["publishedAt"])
                if last_updated < published_at_datetime:
                    images = []
                    file_paths = []
                    if item.get("images") is not None:
                        images += [image for image in item.get("images")]
                    if item.get("video") is not None:
                        file_path = download_video_to_local(
                            video_url=f"https://media.static.bstage.in/{artist}" + item["video"]["hlsPath"]["path"],
                            filename=f"{time.time()}.mp4"
                        )
                        file_paths.append(file_path)
                    social_post = SocialPost(
                        post_link=f"https://{artist}.bstage.in/story/feed/{item['typeId']}",
                        author=PostAuthor(item["author"]["nickname"], item["author"]["avatarImgPath"]),
                        text=item["description"],
                        images=images,
                        file_paths=file_paths,
                        created_at=published_at_datetime)
                    print(social_post)
                    social_posts.append(social_post)
                else:
                    break

            post_count = len(social_posts)
            if post_count != 0:
                print(f"有 {post_count} 則發文")
                for social_post in reversed(social_posts):
                    post_message(
                        channel_id=discord_channel_id,
                        content=social_post.post_link,
                        embeds=build_embeds(social_post),
                        file_paths=social_post.file_paths
                    )
                    cleanup_local_files(social_post.file_paths)
                # 儲存最新發文時間
                updated_at = max([social_post.created_at for social_post in social_posts])
                print(f"更新最後發文時間: {updated_at}")
                await self.__firestore.set_updated_at(SocialPlatform.BSTAGE, artist, updated_at)
            else:
                print("無新發文")
            print("抓取結束")

        mnet_plus_subscribed_list = await self.__firestore.get_subscribed_list(SocialPlatform.MNET_PLUS)
        for doc in mnet_plus_subscribed_list:
            # 每隔 3 ~ 5 秒執行
            random_sleep_time = random.uniform(3, 5)
            time.sleep(random_sleep_time)
            artist = doc.id
            discord_channel_id = doc.get("discord_channel_id")
            # 取得上次最新發文時間
            last_updated = doc.get("updated_at")
            print(f"{artist} 上次發文時間: {last_updated}")
            print("開始抓取資料...")
            request = requests.get(headers=headers,
                                   url=f"https://artist.mnetplus.world/svc/stg/{artist}/home/api/v1/home/star/feeds")
            data = json.loads(request.text)

            social_posts = []
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
                    social_post = SocialPost(
                        post_link=f"https://artist.mnetplus.world/main/stg/{artist}/story/feed/{item['typeId']}",
                        author=PostAuthor(item["author"]["nickname"], item["author"]["avatarImgPath"]),
                        text=item["description"], images=images, videos=videos,
                        created_at=published_at_datetime)
                    social_posts.append(social_post)
                else:
                    break

            post_count = len(social_posts)
            if post_count != 0:
                print(f"有 {post_count} 則發文")
                for social_post in reversed(social_posts):
                    post_message(
                        channel_id=discord_channel_id,
                        content=social_post.post_link,
                        embeds=build_embeds(social_post)
                    )

                    videos = social_post.videos
                    if videos is not None and len(videos) > 0:
                        file_paths = []
                        for video in videos:
                            file_path = download_m3u8_to_mp4(video, f"{time.time()}.mp4")
                            file_paths.append(file_path)

                        # 直接傳入檔案路徑列表
                        post_message(
                            channel_id=discord_channel_id,
                            content="",
                            file_paths=file_paths  # 直接傳入路徑列表
                        )

                        # 清理暫存檔案
                        for file_path in file_paths:
                            if os.path.exists(file_path):
                                os.remove(file_path)
                # 儲存最新發文時間
                updated_at = max([social_post.created_at for social_post in social_posts])
                print(f"更新最後發文時間: {updated_at}")
                await self.__firestore.set_updated_at(SocialPlatform.MNET_PLUS, artist, updated_at)
            else:
                print("無新發文")
            print("抓取結束")


if __name__ == '__main__':
    file_paths = []
    file_path = download_m3u8_to_mp4(
        "https://media.static.bstage.in/limelight/media/68c166446b9b4960d49eac08/hls/ori.m3u8", f"{time.time()}.mp4")
    file_paths.append(file_path)
