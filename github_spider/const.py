# -*- coding=utf8 -*-

GITHUB_API_HOST = 'api.github.com'

START_USER = 'LiuRoy'

# API 获取列表最大长度
PAGE_SIZE = 30

TIMEOUT = 20

RETRY_COUNT = 3

MONGO_URI = 'mongodb://localhost:27017'
REDIS_URI = 'redis://localhost:6379'

MONGO_DB_NAME = 'github'

REDIS_VISITED_URLS = 'visited_urls'


class MongodbCollection(object):
    """
    用到的mongodb collection名称
    """
    USER = 'user'
    REPO = 'repo'
    USER_REPO = 'user_repo'
    FOLLOWER = 'follower'
    FOLLOWING = 'following'
