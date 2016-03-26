# -*- coding=utf8 -*-
"""
    消费者
"""


class Consumer(object):
    """
    消费者公共类
    """
    def __init__(self):
        pass

    def sync_get(self):
        """
        同步发送发送
        """
        pass

    def consume(self):
        pass


class UserConsumer(Consumer):
    """
    用户队列消费者
    """
    pass


class RepoConsumer(Consumer):
    """
    repo队列消费者
    """
    pass


class FollowConsumer(Consumer):
    """
    用户关系消费者
    """
    pass
