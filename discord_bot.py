from discord import Embed, message

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