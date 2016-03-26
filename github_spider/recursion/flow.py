# -*- coding=utf8 -*-
"""
    流程控制
"""
import logging

from github_spider.const import (
    REDIS_VISITED_URLS,
    MongodbCollection,
)
from github_spider.recursion.worker import (
    mongo_save_entity,
    mongo_save_relation,
)
from github_spider.extensions import redis_client
from github_spider.utils import (
    gen_user_repo_url,
    gen_user_following_url,
    gen_user_follwer_url,
    gen_url_list,
    gen_user_page_url,
    check_url_visited,
)

LOGGER = logging.getLogger(__name__)


def request_api(urls, method, callback, **kwargs):
    """请求API数据

    Args:
        urls (list): 请求url列表
        method (func): 请求方法
        callback (func): 回调函数
    """
    unvisited_urls = check_url_visited(urls)
    if not unvisited_urls:
        return

    try:
        bodies = method(unvisited_urls)
    except Exception as exc:
        LOGGER.exception(exc)
    else:
        redis_client.sadd(REDIS_VISITED_URLS, *unvisited_urls)
        map(lambda body: callback(body, method, **kwargs), bodies)


def parse_user(data, method):
    """解析用户数据

    Args:
        data (dict): 用户数据
        method (func): 请求方法
    """
    if not data:
        return

    user_id = data.get('login')
    if not user_id:
        return

    user = {
        'id': user_id,
        'type': data.get('type'),
        'name': data.get('name'),
        'company': data.get('company'),
        'blog': data.get('blog'),
        'location': data.get('location'),
        'email': data.get('email'),
        'repos_count': data.get('public_repos', 0),
        'gists_count': data.get('public+gists', 0),
        'followers': data.get('followers', 0),
        'following': data.get('following', 0),
        'created_at': data.get('created_at')
    }
    mongo_save_entity.delay(user)
    follower_urls = gen_url_list(user_id, gen_user_follwer_url,
                                 user['followers'])
    following_urls = gen_url_list(user_id, gen_user_following_url,
                                  user['following'])
    repo_urls = gen_url_list(user_id, gen_user_repo_url, user['repos_count'])

    request_api(repo_urls, method, parse_repos, user=user_id)
    request_api(following_urls, method, parse_follow,
                user=user_id, kind=MongodbCollection.FOLLOWING)
    request_api(follower_urls, method, parse_follow,
                user=user_id, kind=MongodbCollection.FOLLOWER)


def parse_repos(data, method, user=None):
    """解析项目数据

    Args:
        data (list): 用户数据
        method (func): 请求函数
        user (string): 用户
    """
    if not data:
        return

    user = user or data[0].get('owner', {}).get('login')
    if not user:
        return

    repo_list = []
    for element in data:
        # fork的项目不关心
        if element.get('fork'):
            continue

        repo = {
            'id': element.get('id'),
            'name': element.get('full_name'),
            'description': element.get('description'),
            'size': element.get('size'),
            'language': element.get('language'),
            'watchers_count': element.get('watchers_count'),
            'fork_count': element.get('fork_count'),
        }
        repo_list.append(repo['name'])
        mongo_save_entity.delay(repo, False)
    mongo_save_relation.delay({'id': user, 'list': repo_list},
                              MongodbCollection.USER_REPO)


def parse_follow(data, method, kind=MongodbCollection.FOLLOWER, user=None):
    """解析关注关系

     Args:
        data (list): 请求数据
        method (func): 请求函数
        kind (string): 是关注的人还是关注着
        user (string): 用户
    """
    if not data or not user:
        return

    users = []
    urls = []
    for element in data:
        users.append(element.get('login'))
        urls.append(gen_user_page_url(element.get('login')))

    mongo_save_relation.delay({'id': user, 'list': users}, kind)
    request_api(urls, method, parse_user)
