# -*- coding=utf8 -*-
"""
    数据访问
"""
from pymongo import MongoClient
from redis import Redis

from github_spider.const import MONGO_DB_NAME
from github_spider.settings import (
    MONGO_URI,
    REDIS_URI
)

mongo_client = MongoClient(MONGO_URI)
redis_client = Redis.from_url(REDIS_URI)

mongo_db = mongo_client[MONGO_DB_NAME]
