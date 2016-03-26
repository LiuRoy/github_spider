# -*- coding=utf8 -*-

GITHUB_API_HOST = 'api.github.com'

# API 获取列表最大长度
PAGE_SIZE = 30

MONGO_DB_NAME = 'github'

REDIS_VISITED_URLS = 'visited_urls'

PROXY_KEY = 'proxy_zset'

HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate, sdch',
    'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6,zh-TW;q=0.4',
    'Cache-Control': 'no-cache',
    'Connection':'keep-alive',
    'Host':'api.github.com',
    'Pragma':'no-cache',
    'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) '
                 'AppleWebKit/537.36 (KHTML, like Gecko) '
                 'Chrome/49.0.2623.87 Safari/537.36'
}


class MongodbCollection(object):
    """
    用到的mongodb collection名称
    """
    USER = 'user'
    REPO = 'repo'
    USER_REPO = 'user_repo'
    FOLLOWER = 'follower'
    FOLLOWING = 'following'
