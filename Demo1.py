# -*- coding:utf-8 -*-
import itchat
from itchat.content import *
import requests
import json
import time
import os

'''
msg['Type']:消息类型
msg['Text']:消息文本内容
msg['ToUserName']:消息接收者
msg['FromUserName']:消息发起者
msg['content']:文本消息
msg['FileName']:文件名字，如果是自带的表情就会显示表情
1、给自己发送消息只需要发出消息，不指定发送者，默认发给自己(登录者):
    itchat.send_msg('nice to meet you')
2、发送图片,ToUser不指定时发给自己
    itchat.send_image(ImageName.decode('utf-8'),ToUser)
3、发送视频 
    itchat.send_video(VideoName.decode('utf-8'),ToUser)
4、发送文件
    itchat.send_file(path.decode(,utf-8,))
'''

text = "欢迎使用柴小运机器人，使用说明如下：\n" \
       "基本功能：聊天对话、问答百科、生活百科、星座运势、新闻资讯、菜谱、查快递、中英互译、数字计算、" \
       "讲故事、脑筋急转弯、绕口令、成语接龙、实时路况、天气查询等等，更多功能正在完善，其它功能如下：\n" \
       "    1、回复'#':查看帮助信息\n" \
       "    2、如果需要给我的主人留言，请在留言前面加'@',主人会尽快回复的\n" \
       "    3、还有什么不懂得，向我提问吧！[愉快][愉快]\n" \
       "注意：这属于个人微信号，不是公众号，所以不能一直在线，晚上十二点到第二天早上七点之间偶是需要休息的[睡][睡]"


def getFriendName(user_ID):  # 根据发送者的ID找到对应的昵称
    friend = itchat.search_friends(userName=user_ID)
    return friend['RemarkName']


# 以下函数为自动回复信息
# 处理文本消息
@itchat.msg_register(TEXT)  # 只会接收文本信息
def reply_text(msg):
    from_text = msg['Text']
    user_name_ID = msg['FromUserName']
    if getFriendName(user_name_ID) == '马富强':
        return
    if msg['ToUserName'] == 'filehelper':
        if from_text == '#':
            itchat.send(text, 'filehelper')
        else:
            itchat.send('机器人：' + tuling(from_text), 'filehelper')
        return

    if from_text == '#':  # 查看帮助
        itchat.send(text, user_name_ID)
        return
    if from_text[0] == '@':  # 留言
        if getFriendName(user_name_ID) != '':
            itchat.send('From:' + getFriendName(user_name_ID) + '\n   ' + from_text[1:], 'filehelper')
        return

    to_text = tuling(from_text)  # 调用图灵机器人知识库，参数是收到对方的消息，返回图灵机器人回复的内容
    itchat.send('机器人：' + to_text, user_name_ID)


# 处理多媒体消息  图片 声音 文件 视频
@itchat.msg_register([PICTURE, RECORDING, ATTACHMENT, VIDEO])
def download_files(msg):
    to_text = '不好意思哈，请发送文本内容，无法识别图片、声音、文件和视频，但主人赋予我模仿的权利....[呲牙][呲牙]'
    msg['Text'](msg['FileName'])
    if msg['Type'] == 'Picture':
        if msg['MsgType'] != 3:
            itchat.send('这种表情偶无法识别呀T^T[难过][难过]', msg['FromUserName'])
            os.remove(msg['FileName'])
            return
        itchat.send_image(msg['FileName'], msg['FromUserName'])
        time.sleep(2)
    else:
        itchat.send_file(msg['FileName'], msg['FromUserName'])
        time.sleep(2)

    itchat.send(to_text, msg['FromUserName'])
    os.remove(msg['FileName'])


# 收到好友邀请自动添加好友
@itchat.msg_register(FRIENDS)
def add_friend(msg):
    itchat.add_friend(**msg['Text'])  # 该操作会自动将新好友的消息录入，不需要重载通讯录
    itchat.send_msg(text, msg['RecommendInfo']['UserName'])


# 在注册时增加isGroupChat=True将判定为群聊回复
@itchat.msg_register(TEXT, isGroupChat=True)
def text_reply(msg):
    if msg['isAt']:
        from_text = msg['Content']
        itchat.send(u'@%s\u2005 %s' % (msg['ActualNickName'], tuling(from_text)), msg['FromUserName'])

# 调用图灵机器人
def tuling(info):
    appkey = "24900f8a12014850800c0cc9c91457ad"
    url = "http://www.tuling123.com/openapi/api?key=%s&info=%s" % (appkey, info)
    req = requests.get(url)
    content = req.text
    data = json.loads(content)
    answer = data['text']
    return answer


# 百度翻译
def baidu_trans(info):
    url = 'http://fanyi.baidu.com/v2transapi'
    keywords = {
        'from': 'zh',
        'to': 'en',
        'query': info,
    }
    req = requests.post(url, keywords)
    data = req.json()
    try:
        result = data['dict_result']['simple_means']['word_means']
        return ';'.join(result)
    except:
        return data['trans_result']['data'][0]['dst']


def main():
    itchat.auto_login(hotReload=True)  # 微信登录，即使程序关闭，一定时间内重新开启也可以不用重新扫码
    itchat.run()


if __name__ == '__main__':
    main()
