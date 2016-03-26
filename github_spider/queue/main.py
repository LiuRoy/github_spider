# -*- coding=utf8 -*-
"""
    主函数
"""
from multiprocessing import Process

from github_spider.queue.consumer import consumer_list
from github_spider.queue.producer import url_sender
from github_spider.extensions import redis_client
from github_spider.settings import START_USER
from github_spider.const import REDIS_VISITED_URLS, RoutingKey
from github_spider.utils import gen_user_page_url

if __name__ == '__main__':
    redis_client.delete(REDIS_VISITED_URLS)
    start_user_url = gen_user_page_url(START_USER)
    url_sender.send_url(start_user_url, RoutingKey.USER)

    # user_consumer = consumer_list[0]
    # user_consumer.run()
    process_list = map(lambda x: Process(target=x.run), consumer_list)
    map(lambda p: p.start(), process_list)
    map(lambda p: p.join(), process_list)
