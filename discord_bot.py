import json
import os

import requests
from discord import Embed, SyncWebhook

from sns_info import SnsInfo


def generate_embeds(sns_info: SnsInfo):
    embeds = []
    # 圖片訊息，Embed 的 url 如果一樣，最多可以 4 張以下的合併在一個區塊
    for index, image_url in enumerate(sns_info.images[slice(4)]):
        if index == 0:
            embed = (
                Embed(title=sns_info.title, description=sns_info.content, url=sns_info.post_link,
                      timestamp=sns_info.timestamp).set_author(
                    name=sns_info.profile.name, icon_url=sns_info.profile.url)
                .set_image(url=image_url))
            embeds.append(embed)
        else:
            embeds.append(Embed(url=sns_info.post_link)
                          .set_author(name=sns_info.profile.name, url=sns_info.profile.url)
                          .set_image(url=image_url))
    else:
        embeds.append(Embed(title=sns_info.title, description=sns_info.content, url=sns_info.post_link).set_author(
            name=sns_info.profile.name, icon_url=sns_info.profile.url))
    return embeds


def send_message_by_api(discord_channel_id: str, content: str, embeds=None, files=None):
    if embeds is None:
        embeds = []

    url = f"https://discord.com/api/channels/{discord_channel_id}/messages"

    headers = {
        'Authorization': f'Bot {os.environ["BOT_TOKEN"]}',
    }

    # 如果有檔案，使用 multipart/form-data
    if files is not None and len(files) > 0:
        # 準備 multipart 資料
        data = {
            'content': content,
        }
        if embeds:
            data['embeds'] = json.dumps([embed.to_dict() for embed in embeds])

        # 準備檔案
        files_dict = {}
        for i, file_path in enumerate(files):
            files_dict[f'files[{i}]'] = open(file_path, 'rb')

        try:
            response = requests.post(url, headers=headers, data=data, files=files_dict)
        finally:
            # 關閉所有檔案
            for file_obj in files_dict.values():
                file_obj.close()
    else:
        # 沒有檔案時使用 JSON
        data = {
            "content": content
        }
        if embeds:
            data["embeds"] = [embed.to_dict() for embed in embeds]

        headers['Content-Type'] = 'application/json'
        payload = json.dumps(data)
        response = requests.post(url, headers=headers, data=payload)

    print(response.text)
    return response


class DiscordBot:
    def __init__(self, webhook_url: str):
        self.__webhook = SyncWebhook.from_url(webhook_url)

    def send_message(self, sns_info: SnsInfo):
        self.__webhook.send(content=sns_info.post_link, embeds=generate_embeds(sns_info=sns_info))
