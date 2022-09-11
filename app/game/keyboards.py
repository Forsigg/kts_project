import json

start_keyboard = {
            "one_time": "true",
            "buttons": [
                {
                    "action": {
                        "type": "callback",
                        "payload": "start-game",
                        "label": "Старт игры"
                    }
                }
            ]
        }

start_keyboard = json.dumps(start_keyboard)
