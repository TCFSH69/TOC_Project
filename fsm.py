from transitions.extensions import GraphMachine
import random
from utils import send_text_message, send_image_url, send_button_message, push_message, google_maps_search, get_latitude_longtitude, random_pick, show_nearby, conditional_search, show_restaurant_card
from linebot.models import TextSendMessage, ImageSendMessage, TemplateSendMessage, ImageCarouselColumn, ImageCarouselTemplate, ButtonsTemplate, MessageTemplateAction, URITemplateAction, ImageSendMessage, CarouselTemplate, CarouselColumn

class TocMachine(GraphMachine):
	def __init__(self, lat, lng, rating, min_price, max_price, **machine_configs):
		self.machine = GraphMachine(model=self, **machine_configs)
		self.lat = lat
		self.lng = lng
		self.rating = rating
		self.min_price = min_price
		self.max_price = max_price

	def is_going_to_menu(self, event):
		return True

	def is_going_to_description(self, event):
		text = event.message.text
		return text.lower() == "description"

	def is_going_to_settings(self, event):
		text = event.message.text
		return text.lower() == "settings"

	def is_going_to_set_current_location(self, event):
		text = event.message.text
		return text.lower() == "set current location"

	def is_going_to_receive_location(self, event):
		message = event.message
		if message.type == "location":
			return True
		if message.type == "text":
			lat, lng, _ = get_latitude_longtitude(message.text)
			return ((lat != 200) and (lng != 200))

	def is_going_to_set_rating(self, event):
		text = event.message.text
		return text.lower() == "set rating"

	def is_going_to_receive_rating(self, event):
		message = event.message
		if message.type != "text":
			return False
		try:
			rating = float(message.text)
			assert rating >= 1 and rating <= 5
			return True
		except (ValueError, AssertionError):
			return False

	def is_going_to_set_price(self, event):
		text = event.message.text
		return text.lower() == "set price"

	def is_going_to_receive_price(self, event):
		message = event.message
		if message.type != "text":
			return False
		try:
			min_max = message.text.split()
			assert len(min_max) == 2
			assert min_max[0] in ["1", "2", "3", "4"]
			assert min_max[1] in ["1", "2", "3", "4"]
			assert int(min_max[0]) <= int(min_max[1])
			return True
		except AssertionError:
			return False

	def is_going_to_random_pick(self, event):
		text = event.message.text
		return text.lower() == "random pick"

	def is_going_to_random_pick_nearby(self, event):
		text = event.message.text
		return text.lower() == "random pick nearby"

	def is_going_to_random_pick_tw(self, event):
		text = event.message.text
		return text.lower() == "random pick tw"

	def is_going_to_conditional_search(self, event):
		text = event.message.text
		return text.lower() == "conditional search"

	def is_going_to_search(self, event):
		if event.message.type != "text":
			return False
		text = event.message.text
		params = text.split(",")
		return len(params) in [1, 2]

	def is_going_to_show_nearby(self, event):
		text = event.message.text
		return text.lower() == "show nearby"

	def is_going_to_show_restaurant(self, event):
		text = event.message.text
		return text.lower() == "show restaurant"
	
	def is_going_to_show_restaurant_card(self, event):
		message = event.message
		return message.type == "text"

	def on_enter_description(self, event):
		push_message(event.source.user_id, TextSendMessage(text="哈囉~\n我是美食機器人"))
		push_message(event.source.user_id, TextSendMessage(text="用法說明：\n總共有提供五種功能\n1.設定：設定目前位置、篩選評價與價格\n2.隨機選：提供隨機選擇附近的一間餐廳或全台的一間餐廳\n3.條件搜尋：可輸入關鍵字及範圍來搜尋理想的餐廳\n4.附近餐廳列表：列出若干筆附近的餐廳\n5.顯示地理位置：可輸入地址並以Google Maps開啟\n若要返回主選單，輸入go to menu即可"))
		self.go_to_menu(event)

	def on_enter_menu(self, event):
		userid = event.source.user_id
		url = None
		title = '功能表'
		uptext = '請點擊下方按鈕'
		labels = ['設定', '隨機選', '條件搜尋', '附近餐廳列表']
		texts = ['settings', 'random pick', 'conditional search', 'show nearby']
		send_button_message(userid, url, title, uptext, labels, texts)
		userid = event.source.user_id
		url = None
		title = '功能表'
		uptext = '請點擊下方按鈕'
		labels = ['顯示地理位置', '機器人說明']
		texts = ['show restaurant', 'description']
		send_button_message(userid, url, title, uptext, labels, texts)


	def on_enter_settings(self, event):
		userid = event.source.user_id
		url = None
		title = '設定'
		uptext = '請點擊下方按鈕'
		labels = ['目前位置', '評價', '價格', '返回主選單']
		texts = ['set current location', 'set rating', 'set price', 'go to menu']
		send_button_message(userid, url, title, uptext, labels, texts)

	def on_enter_set_current_location(self, event):
		push_message(event.source.user_id, TextSendMessage(text="請利用:\n1. +號->location\n2.手動輸入地址或所在地\n來設定目前位置"))

	def on_enter_receive_location(self, event):
		message = event.message
		if message.type == "text":
			lat, lng, _ = get_latitude_longtitude(message.text)
		else:
			lat, lng = event.message.latitude, event.message.longitude
		self.lat, self.lng = lat, lng
		send_text_message(event.reply_token, "已設定完成")
		self.go_to_settings(event)

	def on_enter_set_rating(self, event):
		push_message(event.source.user_id, TextSendMessage(text="請輸入評分標準(1~5，整數或小數)"))
	
	def on_enter_receive_rating(self, event):
		message = event.message
		self.rating = "%.1f" % float(message.text)
		send_text_message(event.reply_token, "已設定完成")
		self.go_to_settings(event)

	def on_enter_set_price(self, event):
		push_message(event.source.user_id, TextSendMessage(text="請輸入價格區間(1~4，限整數, e.g. 2 2)"))
	
	def on_enter_receive_price(self, event):
		message = event.message
		min_max = message.text.split()
		self.min_price = int(min_max[0])
		self.max_price = int(min_max[1])
		send_text_message(event.reply_token, "已設定完成")
		self.go_to_settings(event)

	def on_enter_random_pick(self, event):
		userid = event.source.user_id
		url = None
		title = '隨機選餐廳'
		uptext = '請選擇模式'
		labels = ['隨機挑選我附近的餐廳', '隨機挑選全台的餐廳', '返回主選單']
		texts = ['random pick nearby', 'random pick tw', 'go to menu']
		send_button_message(userid, url, title, uptext, labels, texts)

	def on_enter_random_pick_nearby(self, event):
		random_pick(event.source.user_id, self.lat, self.lng, random.randint(500, 2000), 1)
		self.go_to_random_pick(event)

	def on_enter_random_pick_tw(self, event):
		lat = random.randint(2254951000000000, 2510928000000000) / 100000000000000
		lng = random.randint(12044730000000000, 12171950000000000) / 100000000000000
		random_pick(event.source.user_id, lat, lng, 100000, 1)
		self.go_to_random_pick(event)

	def on_enter_conditional_search(self, event):
		send_text_message(event.reply_token, "請輸入餐廳關鍵字(必填)與範圍(單位：公尺)(選填)\n範例：火鍋,1000")

	def on_enter_search(self, event):
		text = event.message.text
		params = text.split(",")
		keyword = params[0]
		radius = random.randint(500, 1500)
		if len(params) == 2:
			radius = int(params[1].strip())
		conditional_search(event.source.user_id, self.lat, self.lng, self.rating, self.min_price, self.max_price, keyword, radius)
		self.go_to_menu(event)

	def on_enter_show_nearby(self, event):
		show_nearby(event.source.user_id, self.lat, self.lng)
		self.go_to_menu(event)

	def on_enter_show_restaurant(self, event):
		send_text_message(event.reply_token, "請輸入餐廳地址")

	def on_enter_show_restaurant_card(self, event):
		address = event.message.text
		show_restaurant_card(event.source.user_id, address)
		self.go_to_menu(event)