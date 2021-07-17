class RssCheck:
    #获取RSS订阅链接信息
    def GetRssData(RssLink):
        import feedparser
        try:
            rss_data = feedparser.parse(RssLink)
            AllList = [{'title': entry['title'], 'link': entry['link'], 'author': entry['author'],
                             'magnet': ((entry['links'])[1])['href']} for entry in rss_data['entries']]
            return AllList
        except:
            print('getRssData Error')
            return 'Error'

    #从数据中筛选出符合的
    def EPcheck(List, author, nowEP, EPregular, CHS_Tregular):
        import re
        try:
            newList = []
            for i in List:
                if i['author'] == author:
                    EP_search = re.search(EPregular, i['title'])
                    if EP_search != None:
                        EP = (EP_search.group())[1:-1]
                        if EP[0] == '0':
                            EP = int(EP[1:])
                        if EP > nowEP:
                            if CHS_Tregular == 'NULL':
                                print('找到符合的\n'+str(i))
                                newList.append(i)
                            else:
                                CHS_T = re.search(CHS_Tregular, i['title'])
                                if CHS_T != None:
                                    print('CHS_找到符合的\n' + str(i))
                                    newList.append(i)
            return newList
        except:
            print('EPcheck Error')
            return 'Error'