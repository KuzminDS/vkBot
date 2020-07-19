import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_bot import VkBot

token = "/your vk group token/"

bot = VkBot(token)
bot.start_bot()