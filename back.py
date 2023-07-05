from datetime import datetime

import vk_api

from config import access_token, community_token
from vk_api.utils import get_random_id
from vk_api.longpoll import VkLongPoll, VkEventType


class VkTools():

    def __init__(self, community_token, access_token):
        self.interface = vk_api.VkApi(token=community_token)
        self.api = vk_api.VkApi(token=access_token)

    def message_send(self, user_id, message, attachment=None):
        self.interface.method('messages.send',
                              {'user_id': user_id,
                               'message': message,
                               'attachment': attachment,
                               'random_id': get_random_id()
                               }
                              )

    def get_profile_info(self, user_id):
        info, = self.api.method('users.get',
                                {'user_id': user_id,
                                 'fields': 'city,bdate,sex,relation'
                                 }
                                )
        user_info = {'name': info['first_name'] + ' ' + info['last_name'],
                     'id': info['id'],
                     'bdate': info['bdate'] if 'bdate' in info else None,
                     'sex': info['sex'] if 'sex' in info else None,
                     'city': info['city']['title'] if 'city' in info else None
                     }
        return user_info

    def search_users(self, params, id, offset):
        if params is None:
            self.message_send(id, f'Здравствуйте, для начала Вам нужно воспользоваться командой "данные", чтобы проверить наличие всех нужных данных')
        else:
            sex = 1 if params['sex'] == 2 else 2
            city = params['city']
            current_year = datetime.now().year
            user_year = int(params['bdate'].split('.')[2])
            age = current_year - user_year
            age_from = age - 5
            age_to = age + 5

            users = self.api.method('users.search',
                                    {'count': 50,
                                     'offset': offset,
                                     'age_from': age_from,
                                     'age_to': age_to,
                                     'sex': sex,
                                     'hometown': city,
                                     'status': 6,
                                     'is_closed': False
                                     }
                                    )
            try:
                users = users['items']
            except KeyError:
                return []

            res = []

            for user in users:
                if user['is_closed'] == False:
                    res.append({'id': user['id'],
                                'name': user['first_name'] + ' ' + user['last_name']
                                }
                               )

            return res if res else None

    def get_photos(self, user_id):
        photos = self.api.method('photos.get',
                                 {'user_id': user_id,
                                  'album_id': 'profile',
                                  'extended': 1
                                  }
                                 )
        try:
            photos = photos['items']
        except KeyError:
            return []

        res = []

        for photo in photos:
            res.append({'owner_id': photo['owner_id'],
                        'id': photo['id'],
                        'likes': photo['likes']['count'],
                        'comments': photo['comments']['count'],
                        }
                       )

        res.sort(key=lambda x: x['likes'] + x['comments'] * 10, reverse=True)
        selected_photos = res[:3]
        return selected_photos


if __name__ == '__main__':
    bot = VkTools(community_token, access_token)
    print(bot.get_profile_info(747529034))
