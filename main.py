# 导入
from DrissionPage import Chromium,ChromiumOptions
from DrissionPage.common import Settings
from datetime import datetime
import configparser
import os
import sys

def exit_with_prompt(msg="程序异常退出"):
    """显示提示信息并等待用户按回车键退出"""
    print(msg)
    input("按回车键退出...")
    sys.exit(1)

#---------------------------------------------------配置文件读取
CONFIG_FILE = 'config.ini'
CONFIG_TEMPLATE = '''# BIPT自动登录配置文件
# 请按以下格式填写用户名和密码
# 行内 # 开头为注释

[credentials]
username = 你的学号
password = 你的密码
'''

def load_config():
    print(">>读取配置文件")
    """读取配置文件，如不存在则创建空白配置文件"""
    if not os.path.exists(CONFIG_FILE):
        print(f"未找到配置文件 {CONFIG_FILE}，已创建空白文件")
        print("请修改配置文件填写用户名和密码")
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            f.write(CONFIG_TEMPLATE)
        exit_with_prompt(" ")

    config = configparser.ConfigParser()
    try:
        config.read(CONFIG_FILE, encoding='utf-8')
    except Exception as e:
        print(f"错误: 配置文件格式不正确 - {e}")
        exit_with_prompt(" ")

    # 检查必要字段
    if not config.has_section('credentials'):
        print("错误: 配置文件缺少 [credentials] 节点")
        print("正确的配置文件格式:")
        print("[credentials]")
        print("username = 你的学号")
        print("password = 你的密码")
        exit_with_prompt(" ")

    if not config.has_option('credentials', 'username') or not config.has_option('credentials', 'password'):
        print("错误: 配置文件缺少 username 或 password 字段")
        exit_with_prompt(" ")

    user_val = config.get('credentials', 'username').strip()
    pwd_val = config.get('credentials', 'password').strip()

    # 检查是否为填写提示
    if user_val in ['你的学号', ''] or pwd_val in ['你的密码', '']:
        print("错误: 请在配置文件中填写真实的用户名和密码")
        exit_with_prompt(" ")


    return user_val, pwd_val




#----------------------------------------------------函数定义
def Check():#重复链接百度 2 次，连的上返回1，两次连不上就返回0
    print(">>外网连接测试")
    for b in range(1,(1+2) ):
        # ↓链接测试，等待3秒，只链接1次不重试
        baidu = tab.get(url = 'https://www.baidu.com',timeout = float(3),retry = 0)
        if baidu:#连的上百度就啥也不干
            print("连接测试成功")
            return True
        else:
            print("已连接失败",b,"次")
    print('没网开始登录')
    return False

def LoginDecide():#两种网络状态，不同登录策略
    print(">>读取校园网登陆状态")
    max_attempts = 3  # 最大尝试次数
    attempt_count = 0  # 当前尝试次数

    while(1):
        tab.get('http://210.31.32.126/srun_portal_success?ac_id=2&theme=pro')
        browser.wait(second = 1)
        #获取两个按钮元素状态，用于判断目前是登录了还是没登录
        out = tab.ele(locator = '#logout',timeout = float(5))
        login = tab.ele(locator = '#login-account',timeout = float(5))


        if (not out)and(login):#没登出有登录按钮，就需要登录  #直接登录
            print('未登陆无网络->直接登陆')
            LoginDef()

        else:#先注销再登录
            print('已登陆但无网络->先注销再登陆')
            print('点击注销按钮')
            out.click(by_js = 1)
            print('done')
            sure = tab.ele('@text()=确认')
            sure.click(by_js = 1)

            tab.get('http://210.31.32.126/srun_portal_success?ac_id=2&theme=pro')
            login = tab.ele(locator = '#login-account',timeout = float(5))

            LoginDef()

        #---------------------密码错误检测
        error_tip = tab.ele(locator = 'E2901: (Third party 1)',timeout = float(2))
        if error_tip:
            exit_with_prompt("疑似密码错误，请检查配置")
        #---------------------学号错误检测
        error_tip = tab.ele(locator = 'E2901: (Third party -200)',timeout = float(2))
        if error_tip:
            exit_with_prompt("疑似学号错误，请检查配置")

        #---------------------联网检测
        baidu = tab.get(url = 'https://www.baidu.com',timeout = float(5),interval = 0)
        if baidu:
            print("成功联网")
            break
        else:
            attempt_count += 1
            print(f"联网失败，第{attempt_count}次尝试")
            if attempt_count >= max_attempts:
                exit_with_prompt("无法连接，我觉得不是我程序的问题了。。。。")

def LoginDef():#登录用函数
    print(">>进行登陆操作")
    tab.get('http://210.31.32.126/srun_portal_success?ac_id=4&theme=pro')
    browser.wait(second = 1)
    login = tab.ele(locator = '#login-account',timeout = float(5))

    print('输入账户密码')
    username = tab.ele(locator = '#username')
    username.click(by_js = 1);
    username.input(vals = user,clear = 1)
    browser.wait(second = 0.5)

    password = tab.ele('#password')
    password.click(by_js = 1);
    password.input(vals = pwd,clear = 1)
    print('done')
    browser.wait(second = 0.5)

    print('点击登录按钮')
    login.click(by_js =1)
    print('done')
    print('登陆流程结束,等待检查网络连接')
    browser.wait(second = 1)

#----------------------------------------------------main

#---------------------------------------------------一些不要动的东西,
#包括程序前期配置，需要global的东西
current_time = datetime.now()
print("当前时间",current_time.strftime("\n%Y-%m-%d %H:%M:%S"))
print("1.确保安装了chrome")
print("2.确保关闭网络代理使用")
print("3.项目开源地址：https://github.com/akic404/BIPT_NET_AUTO_LOGIN")
# print("version212213")



#co = ChromiumOptions().set_browser_path('/opt/google/chrome/google-chrome')
co = ChromiumOptions().headless()
browser = Chromium(co)

tab = browser.latest_tab
user, pwd = load_config()
if Check():
    pass
else:
    LoginDecide()


