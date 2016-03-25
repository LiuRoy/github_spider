# -*- coding=utf8 -*-
"""
    异步任务
"""
from celery import Celery
from github_spider.const import MongodbCollection, BROKER_URI
from github_spider.extensions import mongo_db

app = Celery('write_mongo', broker=BROKER_URI)


@app.task
def mongo_save_entity(entity, is_user=True):
    """把user或repo信息写入mongo

    Args:
        entity (dict): 数据
        is_user (bool): 用户数据还是项目数据
    """
    collection_name = MongodbCollection.USER \
        if is_user else MongodbCollection.REPO
    mongo_collection = mongo_db[collection_name]
    mongo_collection.update({'id': entity['id']}, entity, upsert=True)


@app.task
def mongo_save_relation(entity, relation_type):
    """把用户与用户或用户与项目的关系写入mongo

    Args:
        entity (dict): 数据
        relation_type (bool): 关系类型
    """
    mongo_collection = mongo_db[relation_type]
    data = mongo_collection.find_one({'id': entity['id']})
    if not data:
        mongo_collection.insert(entity)
    else:
        origin_list = entity['list']
        new_list = data['list']
        data['list'] = list(set(origin_list) | set(new_list))
        mongo_collection.update({'id': entity['id']}, data)
