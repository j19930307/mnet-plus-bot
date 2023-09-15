import json
from datetime import datetime
import pytz  # 用于处理时区信息

import requests
from DiscordMessge import Message, Embed, Image, Author

from deta import Deta  # Import Deta


def is_datetime_before_current(datetime_string):
    # 解析日期时间字符串
    date_format = "%Y-%m-%dT%H:%M:%S.%fZ"
    parsed_date = datetime.strptime(datetime_string, date_format)

    # 获取当前时间，并设置为UTC时区
    current_time = datetime.now(pytz.utc)

    # 将 parsed_date 转换为带有时区信息的 datetime 对象
    parsed_date = pytz.utc.localize(parsed_date)

    # 比较日期时间
    return parsed_date > current_time


# 自定义 JSON 编码函数
def custom_encoder(obj):
    if isinstance(obj, (Author, Image, Embed, Message)):
        return obj.__dict__
    else:
        raise TypeError("Object is not JSON serializable")


# 發送訊息到 Discord
def send_message(post: dict):
    # Discord Webhook URL，請將 URL 替換為您自己的 Webhook URL

    # 測試
    webhook_url = ('https://discord.com/api/webhooks/1151347257321476116/NBF-JCl3EFpFL2obrKbRDnpoBCdagJcRzGNgbl1Cu'
                   '-ZbpIS9o_2tcfCxulMXUS5hFB-K')
    # 正式
    # webhook_url = ('https://discord.com/api/webhooks/1152119906981126174'
    #                '/AE_mVQ_WF_DZowhiS8lDSpcZipiy8lM74z7LflPOzbKfE-auqAKiVbimcb-dkxXooOTK')

    # 获取 "content" 字段的数据
    content_data = post["content"]
    images_url = post.get("images", [])
    nickname = post["writer"]["nickname"]
    profile_image = post["writer"]["profileImage"]
    community_id = post["communityId"]
    post_id = post["id"]

    post_link = f"https://www.mnetplus.world/zh-tw/community/post?postId={post_id}&communityId={community_id}"

    embeds = []

    # 構建要發送的 JSON 數據
    # 文字訊息
    if len(images_url) == 0:
        embeds.append(Embed(Author(nickname, profile_image), content_data))
    elif len(images_url) == 1:
        embeds.append(Embed(Author(nickname, profile_image), content_data, image=Image(images_url[0])))
    else:
        embeds.append(
            Embed(Author(nickname, profile_image), content_data, image=Image(images_url[0]), url=profile_image))
        for i in range(1, len(images_url)):
            embeds.append(Embed(image=Image(images_url[i]), url=profile_image))

    # 圖片訊息，Embed 的 url 如果一樣，最多可以 4 張以下的合併在一個區塊
    # for url in images_url:
    #     embeds.append(Embed(image=Image(url), url=profile_image))

    # 將 JSON 數據轉換為字符串
    data_json = json.dumps(Message(post_link, embeds), default=custom_encoder)
    print(data_json)

    # 使用 POST 請求將消息發送到 Webhook
    response = requests.post(webhook_url, data=data_json, headers={'Content-Type': 'application/json'})

    # 檢查是否成功發送消息
    if response.status_code == 204:
        print('消息已成功發送到 Discord 頻道！')
    else:
        print('消息發送失敗。HTTP 響應碼：', response.status_code)
        print('響應內容：', response.text)


# read text file from last_updated.txt
# def read_last_updated():
#     with open('last_updated.txt', 'r') as f:
#         created_time = f.read()
#         f.close()
#         return created_time

def read_last_updated():
    # Initialize
    deta = Deta()
    # This how to connect to or create a database.
    db = deta.Base("ment_plus")
    if db.get("last_updated") is None:
        db.put({"last_updated": datetime.now()})


# write text to last_updated.txt
def write_last_updated(text: str):
    with open('last_updated.txt', 'w') as f:
        f.write(text)
        f.close()


def compare_times(time_str1, time_str2):
    # 將時間字符串轉換為datetime對象
    time1 = datetime.fromisoformat(time_str1[:-1])  # 去掉最後的 'Z' 字符再轉換
    time2 = datetime.fromisoformat(time_str2[:-1])

    # 進行比較並返回結果
    return time1 > time2


def fetch_data():
    query_url = ("https://www.mnetplus.world/api/community-service/v1/community/artist-official-post/list?communityId"
                 "=k82OLwsCyOHT4VUw89NCi&sort=recent&limit=20&offset=0")

    # 'EL7Z UP': 'P8ioxH-hbHoHNGNcI-uEA'
    user_dicts = {'휘서': 'U2YK9yROhTeXjBQgN0K0r', 'Kei': 'iOr32GLOpmaxgr28VRiFX', '예은': '_M7UYPH6_APF0ZkVe0djw',
                  '연희': '16TteD-7QRj8T29n4978X', '나나': 'ngJFcSLDTx_BGBgWeRcB_', '유키': 'KYyBYSC2gC9_R6QnWDQyf'}
    user_ids = list(user_dicts.values())

    print("開始執行...")

    # 讀取最後更新時間
    last_updated = read_last_updated()

    # 将JSON字符串解析为Python对象
    parsed_data = json.loads(requests.get(query_url).text)

    # 新貼文
    new_posts = []

    for post in parsed_data["data"]["posts"]:
        if compare_times(post["createDate"], last_updated):
            if post["writer"]["userId"] in user_ids:
                new_posts.append(post)

    # 讓新推文最後一則發送
    new_posts.reverse()

    for num, post in enumerate(new_posts):
        print("開始發送訊息...")
        send_message(post)
        # 紀錄最新推文的建立時間
        if num == len(new_posts) - 1:
            write_last_updated(post["createDate"])

    print("執行結束")



fetch_data()
