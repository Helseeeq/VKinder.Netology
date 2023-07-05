# импорты
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id

from config import community_token, access_token
from back import VkTools
from db import check_user, add_user, engine


class BotInterface():

    def __init__(self, community_token, access_token):
        self.interface = vk_api.VkApi(token=community_token)
        self.api = VkTools(community_token, access_token)
        self.params = None

    def message_send(self, user_id, message, attachment=None):
        self.interface.method('messages.send',
                              {'user_id': user_id,
                               'message': message,
                               'attachment': attachment,
                               'random_id': get_random_id()
                               }
                              )

    def event_handler(self):
        longpoll = VkLongPoll(self.interface)

        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                command = event.text.lower()
                if command == 'старт' or command == 'привет':
                    self.message_send(event.user_id,
                                      f'Здравствуйте, для начала Вам нужно воспользоваться командой "данные", чтобы проверить наличие всех нужных данных.')
                elif command == 'данные':
                    self.params = self.api.get_profile_info(event.user_id)
                    for key, value in self.params.items():
                        if value is None:
                            self.message_send(event.user_id, f'Введите {key}')
                            for event in longpoll.listen():

                                if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                                    user_input = event.text.capitalize()
                                    break

                            self.params[key] = user_input
                    self.message_send(event.user_id,
                                      f'Ваши данные: {self.params}. Теперь Вы можете воспользоваться командой "поиск" для поиска страниц')
                elif command == 'поиск':
                    offset = 0
                    users = []
                    self.process_search_command(users, event, offset)

    def process_search_command(self, users, event, offset):
        if not users:
            users = self.api.search_users(self.params, event.user_id, offset)

        if users:
            user = users.pop()
            if not check_user(engine, event.user_id, user['id']):
                add_user(engine, event.user_id, user['id'])
                profile_link = f'https://vk.com/id{user["id"]}'
                photos_user = self.api.get_photos(user['id'])
                attachment = ''
                for photo in photos_user:
                    attachment += f'photo{photo["owner_id"]}_{photo["id"]},'
                self.message_send(event.user_id,
                                  f'Встречайте {user["name"]} !\n{profile_link}',
                                  attachment=attachment[:-1])
            else:
                offset += 50
                self.process_search_command(users, event, offset)


if __name__ == '__main__':
    bot = BotInterface(community_token, access_token)
    bot.event_handler()
