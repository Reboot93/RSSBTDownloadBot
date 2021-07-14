#import rss_check
import MySQLdb
import time
import telepot
from telepot.loop import MessageLoop
from telepot.delegate import pave_event_space, per_chat_id, create_open
from telepot.namedtuple import ReplyKeyboardMarkup, ReplyKeyboardRemove

conn = MySQLdb.connect(
    host='127.0.0.1',
    port=3306,
    user='root',
    passwd='LOVELIVEsaiko93',
    db='RSS_Sub',
    charset='utf8', )



def Sub_Add(name, link, nowEP, lastEP):
    try:
        cur = conn.cursor()
        sql = "INSERT INTO Sub_list VALUES ('%s','%s','%s','%s')" % (name, link, nowEP, lastEP)
        print(sql)
        cur.execute(sql)
        conn.commit()
        print(ShowSubList(True))
        del sql
        return 'ok'
    except:
        print('error')
        return 'MySQL Error'


def ShowSubList(format):
    List = ''
    try:
        cur = conn.cursor()
        sql = "SELECT * from Sub_list"
        cur.execute(sql)
        results = cur.fetchall()
        if format == True:
            a = 0
            for i in results:
                a += 1
                name = i[0]
                link = i[1]
                nowEP = i[2]
                lastEP = i[3]
                List = List + '========================\n' \
                              '订阅%s：\n' \
                              '--剧集名：%s\n' \
                              '--Rss订阅链接：%s\n' \
                              '--当前集数：%s\n' \
                              '--最终集数：%s\n' \
                              % (a, name, link, nowEP, lastEP)
            List = List + '========================'
            del a, sql
            return List
        else:
            del sql
            return results
    except:
        print('ShowSubList Error')
        return 'ShowSubList Error'


def SubDel(name):
    try:
        cur = conn.cursor()
        sql = "DELETE FROM Sub_list where 番剧 = '%s'" % name
        cur.execute(sql)
        conn.commit()
        print('删除了一个订阅')
        print(ShowSubList(True))
        del sql
        return 'ok'
    except:
        print('SubDel Error')
        return 'SubDel Error'


class RssAdd(telepot.helper.ChatHandler):
    global name, link, nowEP, lastEP

    def __init__(self, *args, **kwargs):
        super(RssAdd, self).__init__(*args, **kwargs)
        self._count = 0
        self.State = 'normal'

    def on_chat_message(self, msg):
        print(msg)
        if msg['text'] == '/rsssubadd':
            self.State = 'SetRssName'
            print('Start Set RSS_Sub, Username:%s' % (msg['from'])['username'])
            self.sender.sendMessage('请输入要订阅的番剧名称', reply_markup=ReplyKeyboardRemove())
        elif msg['text'] == '/showlist':
            self.list = ShowSubList(True)
            print(self.list)
            if len(self.list) > 0:
                self.sender.sendMessage("目前订阅的番剧有：\n%s" % self.list, reply_markup=ReplyKeyboardRemove())
            else:
                self.sender.sendMessage('当前没有正在订阅的番剧，\n请使用： /rsssubadd  命令添加一个番剧订阅', reply_markup=ReplyKeyboardRemove())
            del self.list
        elif msg['text'] == '/deletesub':
            menu2 = []
            self.State = 'SubDel'
            self.list = ShowSubList(False)
            print(self.list)
            for i in self.list:
                menu = []
                menu.append(i[0])
                menu2.append(menu)
            print(menu2)
            self.list = ShowSubList(True)
            mark_up = ReplyKeyboardMarkup(keyboard=menu2, one_time_keyboard=True, resize_keyboard=True)
            self.sender.sendMessage("这里是目前订阅的番剧信息：\n%s" % self.list, reply_markup=ReplyKeyboardRemove())
            self.sender.sendMessage('请选择需要删除的番剧名称', reply_markup=mark_up)
            del self.list
        elif self.State == 'SetRssName':
            self.name = msg['text']
            print('Set Rss Name: %s' % self.name)
            self.State = 'SetRssLink'
            self.sender.sendMessage('请输入番剧的Rss订阅链接')
        elif self.State == 'SetRssLink':
            self.link = msg['text']
            print('Set Rss Link: %s' % self.link)
            self.State = 'SetRssNowEP'
            self.sender.sendMessage('请输入该番剧已保存集数')
        elif self.State == 'SetRssNowEP':
            self.nowEP = msg['text']
            print('Set Rss NowEP: %s' % self.nowEP)
            self.State = 'SetRssLastEP'
            self.sender.sendMessage('请输入该番剧的最终集数')
        elif self.State == 'SetRssLastEP':
            mark_up = ReplyKeyboardMarkup(keyboard=[['确定'], ['取消']], one_time_keyboard=True, resize_keyboard=True)
            self.lastEP = msg['text']
            print('Set Rss LastEP: %s' % self.lastEP)
            self.State = 'SetRssCheck'
            self.sender.sendMessage(
                '番剧名称：%s\nRss链接：%s\n已保存集数：%s\n最终集数：%s' % (self.name, self.link, self.nowEP, self.lastEP))
            self.sender.sendMessage('以上是新订阅信息，请确认是否添加', reply_markup=mark_up)
        elif self.State == 'SetRssCheck':
            if msg['text'] == '确定':
                self.sender.sendMessage('正在添加番剧订阅信息', reply_markup=ReplyKeyboardRemove())
                i = Sub_Add(self.name, self.link, self.nowEP, self.lastEP)
                if i == 'ok':
                    print('SubRss订阅添加成功')
                    self.sender.sendMessage('番剧订阅添加成功')
                    self.sender.sendMessage(ShowSubList(True))
                else:
                    print('SubRss订阅添加失败')
                    self.sender.sendMessage('番剧订阅添加失败，请检查提交的信息/数据库状态/运行环境')

                del i
            else:
                self.sender.sendMessage('取消操作')
            self.State = 'normal'
        elif self.State == 'SubDel':
            self.State = 'normal'
            self.name = msg['text']
            i = SubDel(self.name)
            if i == 'ok':
                self.sender.sendMessage('成功删除了一个番剧订阅', reply_markup=ReplyKeyboardRemove())
                self.list = ShowSubList(True)
                print(self.list)
                if len(self.list) > 0:
                    self.sender.sendMessage("目前订阅的番剧有：\n%s" % self.list)
            else:
                self.sender.sendMessage('删除番剧订阅失败')


bot = telepot.DelegatorBot('1824625177:AAHQ4ID5rGPxlaW-Ckr6iI3LIuVsNtRgXNs',
                           [pave_event_space()(per_chat_id(), create_open, RssAdd, timeout=30)])
MessageLoop(bot).run_as_thread()
print('Listening ...')

# Keep the program running.
while True:
    time.sleep(10000)
