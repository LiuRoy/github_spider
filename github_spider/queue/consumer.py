# -*- coding=utf8 -*-
"""
    消费者
"""
import logging
import functools


import requests
from retrying import retry
from kombu import Connection, Queue
from kombu.mixins import ConsumerMixin

from github_spider.queue.producer import url_sender
from github_spider.extensions import redis_client
from github_spider.worker import (
    mongo_save_entity,
    mongo_save_relation,
)
from github_spider.utils import (
    gen_user_repo_url,
    gen_user_following_url,
    gen_user_follwer_url,
    gen_url_list,
    check_url_visited,
    get_proxy,
    find_login_by_url,
    gen_user_page_url,
)
from github_spider.settings import (
    MESSAGE_BROKER_URI,
    USER_CONSUMER_COUNT,
    FOLLOWER_CONSUMER_COUNT,
    FOLLOWING_CONSUMER_COUNT,
    REPO_CONSUMER_COUNT,
    REQUEST_RETRY_COUNT,
    TIMEOUT
)
from github_spider.const import (
    PROXY_KEY,
    HEADERS,
    REDIS_VISITED_URLS,
    RoutingKey,
    QueueName,
    MongodbCollection
)

LOGGER = logging.getLogger(__name__)
retry_get = retry(stop_max_attempt_number=REQUEST_RETRY_COUNT)(requests.get)


def request_deco(func):
    """
    调用github API的装饰器
    """
    @functools.wraps(func)
    def _inner(self, body, message):
        url = body
        if not check_url_visited([url]):
            message.reject()

        # 当前没有可用的代理仍会队列稍后再请求
        proxy = get_proxy()
        if not proxy:
            message.requeue()

        proxy_map = {'https': 'http://{}'.format(proxy.decode('ascii'))}
        redis_client.zincrby(PROXY_KEY, proxy)
        try:
            response = retry_get(url, proxies=proxy_map, headers=HEADERS,
                                 timeout=TIMEOUT)
        except Exception as exc:
            LOGGER.error('get {} failed'.format(url))
            LOGGER.exception(exc)
            redis_client.zrem(PROXY_KEY, proxy)
            message.requeue()
        else:
            if response.status_code == 200:
                data = response.json()
                if not data:
                    message.reject()
                else:
                    message.ack()
                print 'url:', url, 'body: ', data
                func(self, (url, data), message)
                redis_client.sadd(REDIS_VISITED_URLS, url)
            else:
                message.requeue()

    return _inner


class BaseConsumer(ConsumerMixin):
    """
    消费者公共类
    """
    def __init__(self, broker_url, queue_name, fetch_count=10):
        """初始化消费者

        Args:
            broker_url (string): broker地址
            queue_name (string): 消费的队列名称
            fetch_count (int): 一次消费的个数
        """
        self.queue_name = queue_name
        self.broker_url = broker_url
        self.fetch_count = fetch_count

        self.connection = Connection(broker_url)
        self.queue = Queue(queue_name)

    def handle_url(self, body, message):
        """
        处理队列中的url
        """
        raise NotImplementedError

    def get_consumers(self, Consumer, channel):
        """
        继承
        """
        consumer = Consumer(
            self.queue,
            callbacks=[self.handle_url],
            auto_declare=True
        )
        consumer.qos(prefetch_count=self.fetch_count)
        return [consumer]


class UserConsumer(BaseConsumer):
    """
    用户队列消费者
    """
    @request_deco
    def handle_url(self, body, message):
        """
        解析用户数据
        """
        url, data = body
        user = {
            'id': data.get('login'),
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

        follower_urls = gen_url_list(user['id'], gen_user_follwer_url,
                                     user['followers'])
        following_urls = gen_url_list(user['id'], gen_user_following_url,
                                      user['following'])
        repo_urls = gen_url_list(user['id'], gen_user_repo_url,
                                 user['repos_count'])
        map(lambda x: url_sender.send_url(x, RoutingKey.REPO), repo_urls)
        map(lambda x: url_sender.send_url(x, RoutingKey.FOLLOWING),
            following_urls)
        map(lambda x: url_sender.send_url(x, RoutingKey.FOLLOWER),
            follower_urls)


class RepoConsumer(BaseConsumer):
    """
    repo队列消费者
    """
    @request_deco
    def handle_url(self, body, message):
        """
        解析项目数据
        """
        url, data = body

        user = find_login_by_url(str(url))
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


class FollowConsumer(BaseConsumer):
    """
    用户关系消费者
    """
    def __init__(self, kind, broker_url, queue_name, fetch_count=10):
        """
        kind指是following还是follower
        """
        BaseConsumer.__init__(self, broker_url, queue_name, fetch_count)
        self.kind = kind

    @request_deco
    def handle_url(self, body, message):
        """
        解析人员关系数据
        """
        url, data = body

        user = find_login_by_url(str(url))
        users = []
        urls = []
        for element in data:
            users.append(element.get('login'))
            urls.append(gen_user_page_url(element.get('login')))

        mongo_save_relation.delay({'id': user, 'list': users}, self.kind)
        map(lambda x: url_sender.send_url(x, RoutingKey.USER), urls)

consumer_list = [UserConsumer(MESSAGE_BROKER_URI, QueueName.USER)] * USER_CONSUMER_COUNT + \
                [RepoConsumer(MESSAGE_BROKER_URI, QueueName.REPO)] * REPO_CONSUMER_COUNT + \
                [FollowConsumer(MongodbCollection.FOLLOWER, MESSAGE_BROKER_URI, QueueName.FOLLOWER)] * FOLLOWER_CONSUMER_COUNT + \
                [FollowConsumer(MongodbCollection.FOLLOWING, MESSAGE_BROKER_URI, QueueName.FOLLOWING)] * FOLLOWING_CONSUMER_COUNT
