import openai
from db_utils import DBManager
import hashlib

from utils import convert_messages_to_md

with open('./openapi_token', 'r', encoding='utf-8') as f:
    openai.api_key = f.read()


class Conversation:
    __messages = []
    __template = open("template/dump_template", "r", encoding="utf-8").read()

    def __init__(self, user: str, article_name: str):
        self.user = user
        self.clean()
        self.article_name = article_name
        self.__messages.append(
            {
                "role": "system",
                "content": "you are a Chinese writing assistant named 'Prokofiev Writing System'",
            }
        )

    def send(self, message: str):
        """
        send message to api, yield current generated word count, or -1 if failed

        :param message: message to be sent to
        :return: processed word count
        """
        print(f"{self.user}: {message}")
        self.__messages.append({"role": "user", "content": message})
        message_gen = ''
        try:
            for chunk in openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=self.__messages,
                    stream=True
            ):
                msg = chunk["choices"][0].get("delta", {}).get("content")
                if msg is not None:
                    message_gen += msg
                    yield len(message_gen)
        except Exception as e:
            print(f"Exception: ({type(e).__name__}): {str(e)}")
            yield -1

        self.__messages.append({"role": "assistant", "content": message_gen})
        print(f"{self.user}: OK")

    def clean(self):
        self.__messages = []

    def render_msg(self):
        title = f"《{self.article_name}》"
        return convert_messages_to_md(self.__messages, self.__template).replace('{title}', title)


class UserSystem:
    table_name = "User"
    db_dir = "./user.db"

    def __init__(self):
        self.db_manager = DBManager(self.db_dir)
        self.db_manager.create_table_if_not_exist(self.table_name)

    def add_user(self, user_name, user_pwd: str):
        pwd_md5 = hashlib.md5(user_pwd.encode("utf-8")).hexdigest()
        self.db_manager.push(user_name, pwd_md5, self.table_name)
        self.db_manager.commit()

    def check_user(self, user_name, user_pwd: str):
        pwd_md5 = hashlib.md5(user_pwd.encode("utf-8")).hexdigest()
        usr_info = self.db_manager.select_where(self.table_name, user_name)
        if len(usr_info) == 0:
            return False
        else:
            return pwd_md5 == usr_info[0][2]

    def remove_user(self, user_name: str):
        self.db_manager.remove(user_name, self.table_name)
        self.db_manager.commit()

    def get_all_users(self) -> dict:
        return self.db_manager.select(table_name=self.table_name)
