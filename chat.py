from threading import Semaphore
from uuid import UUID

# from revChatGPT.revChatGPT import Chatbot
from fakebot import Fakebot as Chatbot

config = {
    "email": "sadej11834@ceoshub.com",
    "password": "Fw7Fja6iA#3rhMN"
}

chatbots = [Chatbot(config, conversation_id=None)]
chatbots_semaphore = Semaphore(len(chatbots))


def chat(message: str, conversation_id: str, parent_id: str):
    chatbots_semaphore.acquire()
    bot = chatbots.pop(0)
    bot.parent_id = parent_id
    bot.conversation_id = conversation_id
    response = bot.get_chat_response(message)
    chatbots.append(bot)
    chatbots_semaphore.release()
    return response
