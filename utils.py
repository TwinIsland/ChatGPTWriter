import datetime


def format_msg(article_name, article_constrain: str, article_word, article_style):
    if article_word is None:
        article_word = 400
    if article_constrain is None or len(article_constrain.strip()) == 0:
        return f"生成一篇{article_word}字的文章，文章叫{article_name}"

    return f"生成一篇{article_word}字的文章，文章叫'{article_name}', 风格：{article_style}, 需要注意的是：{article_constrain}"


def convert_messages_to_md(messages: list, template: str) -> str:
    """
    load messages to md, set the first user line to be {title}, remember to replace it

    :param messages: the msg to be converted
    :param template:
    :return: history content
    """

    conversation_md = ""
    first_user_msg_flag = True
    for idx, msg in enumerate(messages):
        cur_content = msg["content"]
        if msg["role"] == "user":
            if first_user_msg_flag:
                first_user_msg_flag = False
                cur_content = "{title}"
            conversation_md += "\n**" + cur_content.strip() + "** \n"
        elif msg["role"] == "assistant":
            conversation_md += f"\n---\n{cur_content}\n\n---"

    out = template.replace("{chat_content}", conversation_md)
    out = out.replace("{date}", str(datetime.datetime.now()))
    return out
