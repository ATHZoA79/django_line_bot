from django.shortcuts import render
from django.http import (
    HttpRequest,
    HttpResponse,
    HttpResponseBadRequest,
    HttpResponseForbidden,
)
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import json

# Linebot modules
from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import MessageEvent, TextSendMessage, ImageSendMessage

line_bot_api = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)
parser = WebhookParser(settings.LINE_CHANNEL_SECRET)


ACTIONS = ["捷運", "發票"]


# Create your views here.
def index(request: HttpRequest):
    # return render(request, "index.html")
    payload = {"name": "ZoA"}
    return HttpResponse(json.dumps(payload))


# 使用POST傳輸並確保csrf token保護
@csrf_exempt
def callback(request: HttpRequest):
    if request.method == "POST":
        signature = request.META["HTTP_X_LINE_SIGNATURE"]
        body = request.body.decode("utf-8")  # 傳輸資料本體(訊息)

        try:
            events = parser.parse(body, signature)
        except InvalidSignatureError:
            return HttpResponseForbidden()
        except LineBotApiError:
            return HttpResponseBadRequest()

        for event in events:
            # 因為是設定為Message api所以只接收訊息資料
            # 主要調整這個程式區塊來改變應用程式功能
            if isinstance(event, MessageEvent):
                message: str = event.message.text

                if "hello" in message.lower():
                    reply_content = TextSendMessage("hello there")
                elif "捷運" in message:
                    if any((keyword in message) for keyword in ["台中", "臺中"]):
                        img_url = "https://upload.wikimedia.org/wikipedia/commons/a/ac/%E5%8F%B0%E4%B8%AD%E6%8D%B7%E9%81%8B%E8%B7%AF%E7%B7%9A%E5%9C%96_%282018.07%29.png"
                    else:
                        img_url = "https://www.taiwank.jp/taipei_routemap.jpg"
                    reply_content = ImageSendMessage(
                        original_content_url=img_url,
                        preview_image_url=img_url,
                    )
                elif "發票" in message:
                    result = invoice()
                    reply_content = TextSendMessage(result)
                else:
                    actions = ", ".join(ACTIONS)
                    reply_content = TextSendMessage("當前指令支援：" + actions)
                # 用line_bot_api回傳訊息
                line_bot_api.reply_message(event.reply_token, reply_content)

        return HttpResponse()
    else:
        return HttpResponseBadRequest()


# routeless functions
import requests
from bs4 import BeautifulSoup as bs


def invoice():
    url = "https://invoice.etax.nat.gov.tw/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    page = requests.get(url, headers=headers)
    page.encoding = "utf-8"
    source = bs(page.text, "lxml")
    trs = source.find("table", class_="etw-table-bgbox etw-tbig").find_all("tr")
    sp_prize = trs[1].find("td").text
    sp_number = trs[1].find(attrs={"headers": "th02"}).find("p").text
    ex_prize = trs[2].find("td").text
    ex_number = trs[2].find(attrs={"headers": "th02"}).find("p").text
    top_prize = trs[3].find("td").text
    top_numbers = [
        number.text.strip()
        for number in trs[3].find(attrs={"headers": "th02"}).find_all("p")[:-1]
    ]
    re_str = f"{sp_prize}:{sp_number}\n{ex_prize}:{ex_number}\n{top_prize}:\n"
    new_top_numbers = ["- " + name for name in top_numbers]
    new_top_numbers = "\n".join(new_top_numbers)
    return re_str + new_top_numbers
