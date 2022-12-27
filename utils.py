import os
import json
import time
import urllib.request
import requests
import random
from linebot import LineBotApi, WebhookParser
from linebot.models import TextSendMessage, ImageSendMessage, TemplateSendMessage, ImageCarouselColumn, ImageCarouselTemplate, ButtonsTemplate, MessageTemplateAction, URITemplateAction, ImageSendMessage, CarouselTemplate, CarouselColumn


channel_access_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", None)
google_maps_api_token = os.getenv("GOOGLE_API_ACCESS_TOKEN", None)


line_bot_api = LineBotApi(channel_access_token)

def send_text_message(reply_token, text):
	line_bot_api.reply_message(reply_token, TextSendMessage(text=text))
	return "OK"

def send_image_url(uid, img_url):
	message = ImageSendMessage(
		original_content_url=img_url,
		preview_image_url=img_url
	)
	line_bot_api.reply_message(uid, message)
	return "OK"

def send_button_message(uid, img, title, uptext, labels, texts):
	acts = []
	for i, lab in enumerate(labels):
		acts.append(
			MessageTemplateAction(
				label=lab,
				text=texts[i]
			)
		)

	message = TemplateSendMessage(
		alt_text='Buttons template',
		template=ButtonsTemplate(
			thumbnail_image_url=img,
			title=title,
			text=uptext,
			actions=acts
		)
	)
	push_message(uid, message)
	return "OK"

def send_restaurant_message(uid, result):
	indexes = result.keys()
	restaurant_name = result['name'] if 'name' in indexes else "未提供"
	google_rating =  result['rating'] if 'rating' in indexes else "未提供"
	google_price = result['price_level'] if 'price_level' in indexes else 0
	lat = result['geometry']['location']['lat']
	lng = result['geometry']['location']['lng']
	address = google_maps_get_address(lat, lng)
	if 'photos' in indexes:
		photo_reference = result['photos'][0]['photo_reference']
		max_width = result['photos'][0]['width']
		img = f"https://maps.googleapis.com/maps/api/place/photo?maxwidth={max_width}&photoreference={photo_reference}&key={google_maps_api_token}"
		img = requests.get(img).url
	else:
		img = ""
	if 'place_id' in indexes:
		place_id = result['place_id']
		map_url = f"https://www.google.com/maps/search/?api=1&query={lat},{lng}&query_place_id={place_id}"
	else:
		map_url = ""
	message = TemplateSendMessage(
		alt_text=restaurant_name,
		template=ButtonsTemplate(
			thumbnail_image_url=img,
			title=restaurant_name,
			text=f"Google Maps 評分：{google_rating}\n地址：{address}\n價位：{'$' * google_price if google_price >= 1 else '未提供'}",
			actions=[
				URITemplateAction(
					label='查看地圖',
					uri=map_url
				)
			]
		)
	)
	try:
		push_message(uid, message)
	except linebot.exceptions.LineBotApiError:
		message.text = f"Google Maps 評分：{google_rating}\n價位：{'$' * google_price if google_price >= 1 else '未提供'}"
		push_message(uid, message)
	return "OK"

def push_message(uid, obj):
    line_bot_api.push_message(uid, obj)
    return "OK"

def get_latitude_longtitude(address):
	# decode url
	address = urllib.request.quote(address)
	url = f"https://maps.googleapis.com/maps/api/geocode/json?address={address}&key={google_maps_api_token}"
	
	while True:
		res = requests.get(url)
		js = json.loads(res.text)

		if js["status"] == "ZERO_RESULTS":
			print("no result")
			return 200, 200
		if js["status"] != "OVER_QUERY_LIMIT":
			time.sleep(1)
			break

	try:
		result = js["results"][0]["geometry"]["location"]
		lat = result["lat"]
		lng = result["lng"]
		assert lat >= 22 and lat <= 27
		assert lng >= 118 and lng <= 122
		return lat, lng, js["results"]
	except AssertionError:
		print("no result")
		return 200, 200, None
	

def google_maps_search(uid, address, lat, lng, keyword, radius):
	if address is not None:
		lat, lng, result = get_latitude_longtitude(address)
		if (lat == 200) or (lng == 200):
			push_message(uid, TextSendMessage(text="無搜尋結果，請嘗試新的輸入"))
			return None

	keyword = urllib.request.quote(keyword)
	url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={lat},{lng}&radius={radius}&type=restaurant&keyword={keyword}&language=zh-TW&key={google_maps_api_token}"
	print(url)
	res = requests.get(url)
	js = json.loads(res.text)
	if js["status"] == "ZERO_RESULTS":
		push_message(uid, TextSendMessage(text="無搜尋結果，請嘗試新的輸入"))
		return None
	else:
		results = js["results"]
		return results

def google_maps_get_address(lat, lng):
	url = f"https://maps.googleapis.com/maps/api/geocode/json?latlng={lat},{lng}&sensor=true&language=zh-TW&key={google_maps_api_token}"
	res = requests.get(url)
	js = json.loads(res.text)
	results = js["results"]
	return results[0]['formatted_address']

def random_pick(uid, lat, lng, radius, max_num):
	results = google_maps_search(uid, None, lat, lng, "", radius)
	if results is None:
		return
	restaurant_num = len(results)
	num = min(restaurant_num, max_num)
	while num > 0:
		num -= 1
		restaurant_num -= 1
		result = results.pop(random.randint(0, restaurant_num))
		send_restaurant_message(uid, result)

def show_nearby(uid, lat, lng):
	results = google_maps_search(uid, None, lat, lng, "", random.randint(500, 1500))
	if results is None:
		return
	r = f""
	for res in results:
		indexes = res.keys()
		google_price = res['price_level'] if 'price_level' in indexes else 0
		rest_lat = res['geometry']['location']['lat']
		rest_lng = res['geometry']['location']['lng']
		address = google_maps_get_address(rest_lat, rest_lng)
		r += f"{res['name']}\nGoogle Maps 評分：{res['rating'] if 'rating' in indexes else '未提供'}\n價位：{'$' * google_price if google_price >= 1 else '未提供'}\n地址：{address}\n\n"
	push_message(uid, TextSendMessage(text=r))

def conditional_search(uid, lat, lng, rating, min_price, max_price, keyword, radius):
	qualified = []
	results = google_maps_search(uid, None, lat, lng, keyword, radius)
	if results is None:
		return
	r = f""
	for res in results:
		indexes = res.keys()
		if 'rating' in indexes and float(res['rating']) < float(rating):
			continue
		google_price = res['price_level'] if 'price_level' in indexes else 0
		if google_price != 0:
			if google_price < min_price or google_price > max_price:
				continue
		rest_lat = res['geometry']['location']['lat']
		rest_lng = res['geometry']['location']['lng']
		address = google_maps_get_address(rest_lat, rest_lng)
		r += f"{res['name']}\nGoogle Maps 評分：{res['rating'] if 'rating' in indexes else '未提供'}\n價位：{'$' * google_price if google_price >= 1 else '未提供'}\n地址：{address}\n\n"
	
	if r == "":
		push_message(uid, TextSendMessage(text="無符合條件的餐廳"))
	else:
		push_message(uid, TextSendMessage(text=r))

def show_restaurant_card(uid, address):
	lat, lng, res = get_latitude_longtitude(address)
	if lat == 200 or lng == 200:
		push_message(uid, TextSendMessage(text="無此餐廳"))
		return

	address = google_maps_get_address(lat, lng)
	print(res)
	place_id = res[0]['place_id']
	map_url = f"https://www.google.com/maps/search/?api=1&query={lat},{lng}&query_place_id={place_id}"
	message = TemplateSendMessage(
		alt_text="點擊「查看地圖」以搜尋餐廳",
		template=ButtonsTemplate(
			text="點擊「查看地圖」以搜尋餐廳",
			actions=[
				URITemplateAction(
					label='查看地圖',
					uri=map_url
				)
			]
		)
	)
	push_message(uid, message)
	return "OK"
