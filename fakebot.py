import json

class Fakebot():
    
    config: json
    conversation_id: str
    parent_id: str
    headers: dict
    conversation_id_prev: str
    parent_id_prev: str

    def __init__(self, config, conversation_id=None, debug=False, refresh=True) -> Exception:
        self.debug = debug
        self.config = config
        self.conversation_id = conversation_id
        self.parent_id = None
        self.refresh = refresh
    
    def get_chat_response(self, message):
        return {
            "message": message
        }
