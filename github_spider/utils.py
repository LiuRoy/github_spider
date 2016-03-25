# -*- coding=utf8 -*-
"""
    工具函数
"""
from github_spider.extensions import redis_client
from github_spider.const import (
    GITHUB_API_HOST,
    PAGE_SIZE,
    REDIS_VISITED_URLS,
)


def gen_user_page_url(user_name):
    """获取用户主页url

    Args:
        user_name (string): github用户id
        page (int): 页号
    """
    return 'https://{}/users/{}'.format(GITHUB_API_HOST, user_name)


def gen_user_follwer_url(user_name, page=1):
    """获取用户粉丝列表url

    Args:
        user_name (string): github用户id
        page (int): 页号
    """
    return 'https://{}/users/{}/followers?page={}'.format(GITHUB_API_HOST,
                                                          user_name, page)


def gen_user_following_url(user_name, page=1):
    """获取用户关注用户列表url

    Args:
        user_name (string): github用户id
        page (int): 页号
    """
    return 'https://{}/users/{}/following?page={}'.format(GITHUB_API_HOST,
                                                          user_name, page)


def gen_user_repo_url(user_name, page=1):
    """获取用户项目列表url

    Args:
        user_name (string): github用户id
        page (int): 页号
    """
    return 'https://{}/users/{}/repos?page={}'.format(GITHUB_API_HOST,
                                                      user_name, page)


def get_short_url(url):
    """
    去掉url前面的https://api.github.com/
    """
    return url[23:-1]


def gen_url_list(user_name, func, count):
    """调用func生成url列表

    Args:
        user_name (string): 用户名
        func (func): 生成函数
        count (int): 总个数
    """
    result = []
    page = 1
    while (page - 1) * PAGE_SIZE < count:
        result.append(func(user_name, page))
        page += 1
    return result


def check_url_visited(urls):
    """
    判断url是否重复访问过
    """
    result = []
    for url in urls:
        short_url = get_short_url(url)
        visited = redis_client.sismember(REDIS_VISITED_URLS, short_url)
        if not visited:
            result.append(url)
    return result
