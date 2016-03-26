# -*- coding=utf8 -*-
"""
    参数设置
"""

# 爬取的第一个用户
START_USER = 'LiuRoy'

# 请求超时时间
TIMEOUT = 10

# mongo配置
MONGO_URI = 'mongodb://localhost:27017'

# redis配置
REDIS_URI = 'redis://localhost:6379'

# rabbitmq 配置
CELERY_BROKER_URI = 'amqp://guest:guest@localhost:5672/'
MESSAGE_BROKER_URI = 'amqp://guest:guest@localhost:5672/'

# 每个代理的最大使用次数
PROXY_USE_COUNT = 100

# 请求失败重试次数
REQUEST_RETRY_COUNT = 5

USER_CONSUMER_COUNT = 1
FOLLOWER_CONSUMER_COUNT = 1
FOLLOWING_CONSUMER_COUNT = 1
REPO_CONSUMER_COUNT = 1
