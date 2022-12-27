from fsm import TocMachine


def create_machine():
	machine = TocMachine(
		states=["user", "menu", "settings", "set_current_location", "receive_location", "set_rating", "receive_rating", "set_price", "receive_price", "random_pick", "random_pick_nearby", "random_pick_tw", "conditional_search", "search", "show_nearby", "show_restaurant", "show_restaurant_card", "description"],
		transitions=[
			{
				"trigger": "advance",
				"source": "user",
				"dest": "menu",
				"conditions": "is_going_to_menu"
			},
			{
				"trigger": "advance",
				"source": "menu",
				"dest": "settings",
				"conditions": "is_going_to_settings"
			},
			{
				"trigger": "advance",
				"source": "menu",
				"dest": "random_pick",
				"conditions": "is_going_to_random_pick"
			},
			{
				"trigger": "advance",
				"source": "menu",
				"dest": "conditional_search",
				"conditions": "is_going_to_conditional_search"
			},
			{
				"trigger": "advance",
				"source": "menu",
				"dest": "show_nearby",
				"conditions": "is_going_to_show_nearby"
			},
			{
				"trigger": "advance",
				"source": "menu",
				"dest": "show_restaurant",
				"conditions": "is_going_to_show_restaurant"
			},
			{
				"trigger": "advance",
				"source": "menu",
				"dest": "description",
				"conditions": "is_going_to_description"
			},
			{
				"trigger": "advance",
				"source": "settings",
				"dest": "set_current_location",
				"conditions": "is_going_to_set_current_location"
			},
			{
				"trigger": "advance",
				"source": "set_current_location",
				"dest": "receive_location",
				"conditions": "is_going_to_receive_location"
			},
			{
				"trigger": "advance",
				"source": "settings",
				"dest": "set_rating",
				"conditions": "is_going_to_set_rating"
			},
			{
				"trigger": "advance",
				"source": "set_rating",
				"dest": "receive_rating",
				"conditions": "is_going_to_receive_rating"
			},
			{
				"trigger": "advance",
				"source": "settings",
				"dest": "set_price",
				"conditions": "is_going_to_set_price"
			},
			{
				"trigger": "advance",
				"source": "set_price",
				"dest": "receive_price",
				"conditions": "is_going_to_receive_price"
			},
			{
				"trigger": "advance",
				"source": "random_pick",
				"dest": "random_pick_nearby",
				"conditions": "is_going_to_random_pick_nearby"
			},
			{
				"trigger": "advance",
				"source": "random_pick",
				"dest": "random_pick_tw",
				"conditions": "is_going_to_random_pick_tw"
			},
			{
				"trigger": "advance",
				"source": "conditional_search",
				"dest": "search",
				"conditions": "is_going_to_search"
			},
			{
				"trigger": "advance",
				"source": "show_restaurant",
				"dest": "show_restaurant_card",
				"conditions": "is_going_to_show_restaurant_card"
			},
			{
				"trigger": "go_to_random_pick", 
				"source": ["random_pick_nearby", "random_pick_tw"], 
				"dest": "random_pick"
			},
			{
				"trigger": "go_to_settings", 
				"source": ["receive_location", "receive_rating", "receive_price"], 
				"dest": "settings"
			},
			{
				"trigger": "go_to_menu", 
				"source": ["user", "menu", "settings", "set_current_location", "receive_location", "set_rating", "receive_rating", "set_price", "receive_price", "random_pick", "random_pick_nearby", "random_pick_tw", "conditional_search", "search", "show_nearby", "show_restaurant", "show_restaurant_card", "description"],
				"dest": "menu"
			}
		],
		initial="user",
		auto_transitions=False,
		show_conditions=True,
		lat=22.995120662971075,
		lng=120.21863279924229,
		rating=0,
		min_price=1,
		max_price=4
	)

	return machine