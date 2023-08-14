#import re
#import requests
import schedule
import threading
import feedparser
import time
from bs4 import BeautifulSoup
#from lxml import etree
from plugins import register, Plugin, Event, logger, Reply, ReplyType
from utils.api import send_txt
import ssl

# 忽略SSL证书错误
ssl._create_default_https_context = ssl._create_unverified_context

@register
class V2EXSub(Plugin):
    name = "v2exchannelsub"

    def __init__(self, config: dict):
        super().__init__(config)
        # 获取rss地址
        self.rss_url = self.config.get("rssurl")  # 将 rss_url 作为实例变量
        # 存储rss已有项目的链接
        self.processed_links = set()
        # 获取初始的 RSS 订阅内容，跳过处理
        feed = feedparser.parse(self.rss_url)
        #print(feed)
        for entry in feed.entries:
            self.processed_links.add(entry.link)
            #print(entry.link)
        
        scheduler_thread = threading.Thread(target=self.start_schedule)
        scheduler_thread.start()

    def did_receive_message(self, event: Event):
        pass

    def will_generate_reply(self, event: Event):
        pass

    def will_decorate_reply(self, event: Event):
        pass

    def will_send_reply(self, event: Event):
        pass

    def help(self, **kwargs) -> str:
        return "v2ex 频道订阅"

    def start_schedule(self):
        schedule.every(13).minutes.do(self.auto_send)
        #while True:
        #    schedule.run_pending()
        #    time.sleep(600)

    def auto_send(self):
        logger.info("Start V2EX Channel Sub")
        single_chat_list = self.config.get("single_chat_list", [])
        group_chat_list = self.config.get("group_chat_list", [])
        content = self.tg_channel_msg()
        for single_chat in single_chat_list:
            send_txt(content, single_chat)
            time.sleep(1)
        for group_chat in group_chat_list:
            send_txt(content, group_chat)
            time.sleep(1)

    def tg_channel_msg(self) -> str:
        
        formatted_msg = ""
        
        try:
            # 解析 RSS 订阅
            feed = feedparser.parse(self.rss_url)
    
            # 遍历订阅的条目，获取最新的消息
            for entry in reversed(feed.entries):
                # 获取消息链接
                entry_link = entry.link
    
                # 如果链接不在已获取消息的集合中，处理消息并添加到集合中
                if entry_link not in self.processed_links:
                    self.processed_links.add(entry.link)  # 使用成员变量
                    print(f"{entry.link} added to the processed list")

                    # 获取消息描述，并进行格式化输出
                    soup = BeautifulSoup(entry.description, 'html.parser')
                    
                    news_title = soup.find('b').get_text()
                    news_link = soup.find('a')['href']
                    
                    if soup.find('blockquote'):
                        summary_content = soup.find('blockquote').get_text()
                        links = soup.find_all('a', href=True)
                        for link in links:
                            summary_content = summary_content.replace(link.get_text(), f'({link["href"]})')
                        formatted_msg += f"【{news_title}】( {news_link} )\n摘要: {summary_content[8:]}"
                    else:
                        formatted_msg += f"【{news_title}】( {news_link} )"

                
    
                    # 打印消息标题和描述
                    #print("标题:", entry_title)
                    #print("描述:", entry_description)
                    #print("=" * 40)
                    formatted_msg += "\n\n-----------------------\n\n"
                    #print(formatted_msg)

        except Exception as e:
            logger.error(f"Error occurred while fetching tg channel msg: {str(e)}")
        return formatted_msg