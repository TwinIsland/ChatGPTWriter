from pywebio.input import *
from pywebio.output import *
from pywebio import start_server, config
from api import Conversation, UserSystem
from functools import partial
from utils import format_msg
from pywebio.session import set_env

user_system = UserSystem()


def check_login_agree(agree):
    if len(agree) == 0:
        return "同意用户协议以继续"


def echo_generate_field(req_msg: str, cov: Conversation, loading_text: str):
    with put_loading(shape="border", color="success"):
        put_text(loading_text)
        put_scope('process')
        status = True
        for word_count in cov.send(message=req_msg):
            if word_count == -1:
                status = False
                break
            with use_scope('process', clear=True):
                put_text(f"已生成字符: {word_count} 个")

    with use_scope("content_field", clear=True):
        if status:
            put_markdown(cov.render_msg())
            echo_toolkit(cov)
        else:
            toast(f"程序异常！", color="warn")
            put_text("！！！程序错误，请联系管理员！！！").style("color: red; font-size: 20px")


def toolkit_callback(cov: Conversation, choice):
    if choice == "end_session":
        remove("toolkit_field")

    elif choice == "reset_session":
        cov.clean()
        remove("content_field")
        toast(f"重置成功！", color="success")
        req = echo_request_body()
        req_msg = format_msg(
            req["article_title"],
            req["article_limit"],
            req["article_word"],
            req["article_style"],
        )
        echo_generate_field(req_msg, cov, loading_text="正在撰写，请耐心等待...")

    elif choice == "modify_msg":
        remove("toolkit_field")
        req_msg = textarea("文章修改意见", rows=3)
        echo_generate_field(req_msg, cov, loading_text="正在修改中...")


def echo_toolkit(cov):
    with use_scope("toolkit_field"):
        put_markdown("""### 小工具：""")
        md_content = cov.render_msg()

        put_table(
            [
                ["Type", "Content"],
                [
                    "对话操作",
                    put_buttons(
                        [
                            {
                                "label": "结束对话",
                                "value": "end_session",
                                "color": "secondary",
                            },
                            {
                                "label": "重置对话",
                                "value": "reset_session",
                                "color": "danger",
                            },
                        ],
                        onclick=partial(toolkit_callback, cov),
                    ),
                ],
                [
                    "文章操作",
                    put_buttons(
                        [{"label": "修改文章", "value": "modify_msg", "color": "primary"}],
                        onclick=partial(toolkit_callback, cov),
                    ),
                ],
                [
                    "日志下载",
                    put_file(
                        "conversation.md", bytes(md_content, "utf-8"), "conversation.md"
                    ),
                ],
            ]
        )


def echo_request_body():
    remove("toolkit_field")
    with use_scope("request_form", clear=True):
        req = input_group(
            "文章需求",
            [
                input("文章标题", name="article_title", required=True),
                input("文章字数", name="article_word", type=NUMBER),
                input("文章限制", name="article_limit"),
                select(
                    "文章风格",
                    name="article_style",
                    options=["正式", "非正式", "诙谐", "含蓄", "普通"],
                ),
            ],
        )
    return req


@config(title="智能文章生成系统", theme='minty')
def main():
    put_markdown("# 智能文章生成系统")
    set_env(output_animation=False)
    with use_scope("rule"):
        put_collapse(
            "用户协议",
            [put_markdown(open("template/rule.md", "r", encoding="utf-8").read())],
            open=False,
        )

    data = input_group(
        "登录",
        [
            input("用户名", name="name", required=True),
            input("密码", name="pwd", type=PASSWORD, required=True),
            checkbox(
                name="agree", options=["勾选此栏目以同意用户协议"], validate=check_login_agree
            ),
        ],
    )

    validate_result = user_system.check_user(
        user_name=data["name"], user_pwd=data["pwd"]
    )
    remove("rule")
    if not validate_result:
        toast("登陆失败", color="error")
        put_markdown(
            f"""
            未能找到用户 ’{data['name']}‘, [返回主页](./)
            """
        )
    else:
        with use_scope("intro"):
            toast(f"登陆成功！", color="success")
            put_markdown(open("template/welcome.md", "r", encoding="utf-8").read())
            put_collapse(
                "详细说明",
                [put_markdown(open("template/help.md", "r", encoding="utf-8").read())],
                open=False,
            )

        req = echo_request_body()

        req_msg = format_msg(
            req["article_title"],
            req["article_limit"],
            req["article_word"],
            req["article_style"],
        )

        cov = Conversation(data["name"], req["article_title"])
        print("start a session: ", cov)

        echo_generate_field(req_msg, cov, loading_text="正在撰写，请耐心等待...")


start_server(main, port=8686, debug=True)
