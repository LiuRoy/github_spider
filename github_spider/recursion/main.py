# -*- coding=utf8 -*-
"""
    主流程
"""
import signal
import gevent

from github_spider.recursion.flow import request_api, parse_user
from github_spider.recursion.request import sync_get, async_get
from github_spider.utils import gen_user_page_url
from github_spider.extensions import redis_client
from github_spider.settings import START_USER
from github_spider.const import REDIS_VISITED_URLS


def main():
    """
    主流程函数
    """
    redis_client.delete(REDIS_VISITED_URLS)
    start_user_url = gen_user_page_url(START_USER)

    gevent.signal(signal.SIGQUIT, gevent.kill)
    request_api([start_user_url], async_get, parse_user)

if __name__ == '__main__':
    main()
