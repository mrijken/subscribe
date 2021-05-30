import dataclasses
import inspect
from typing import Any, Dict, Iterator, List, Optional, Tuple, Type

import collections


class SubscriptionList:
    """A list of Subscriptions. The object to which a `subscriber` can `subscribe`"""

    _subscriptions: Dict[str, List["Subscription"]] = collections.defaultdict(list)

    def __init__(self, id_: str):
        self.id = id_

    def subscribe(self, prio: int = 0):
        """
        Return a decorator to let a subscriber (the decorated object) subscribe
        to a subscription list (self).
        """

        def decorator(decorated_function):
            self._subscriptions[self.id].append(
                Subscription(
                    prio=prio,
                    subscription_list=self,
                    subscriber=decorated_function,
                )
            )
            self._subscriptions[self.id].sort()
            return decorated_function

        return decorator

    def get_subscriptions(self) -> Iterator["Subscription"]:
        """
        Iterate over all subscription in order of priority
        """
        yield from self._subscriptions[self.id]

    @property
    def subscribers(self) -> Iterator[Any]:
        """
        Iterate over all subscribers in order of priority
        """
        yield from self.get_subscribers()

    def get_subscribers(self) -> Iterator[Any]:
        """
        Iterate over all subscribers in order of priority
        """
        for subscription in self._subscriptions[self.id]:
            yield subscription.subscriber

    def call_subscribers(self, *args, **kwargs) -> None:
        """
        Iterate over all subscribers and call them with the
        `kwargs` and `args`.

        Note: This will work only when all subscribers are callables.
        """
        for subscription in self._subscriptions[self.id]:
            subscription.subscriber(*args, *kwargs)

    def __repr__(self) -> str:
        return f"<SubscriptionList id='{self.id}'>"


@dataclasses.dataclass(frozen=True)
class Subscription:
    """
    A single subscription by a `subscriber` to a `subscription_list`
    """

    subscription_list: SubscriptionList
    prio: int
    subscriber: Any

    def __lt__(self, other):
        """
        >>> sl1 = SubscriptionList("1")
        >>> sl2 = SubscriptionList("2")
        >>> Subscription(subscription_list=sl1, prio=1, subscriber=None) < Subscription(subscription_list=sl1, prio=2, subscriber=None)
        True
        >>> Subscription(subscription_list=sl1, prio=2, subscriber=None) < Subscription(subscription_list=sl1, prio=1, subscriber=None)
        False
        >>> Subscription(subscription_list=sl1, prio=1, subscriber=None) < Subscription(subscription_list=sl2, prio=1, subscriber=None)
        True
        >>> Subscription(subscription_list=sl2, prio=1, subscriber=None) < Subscription(subscription_list=sl1, prio=1, subscriber=None)
        False
        >>> Subscription(subscription_list=sl2, prio=1, subscriber=None) < None
        True
        """
        if not isinstance(other, self.__class__):
            return True
        if self.subscription_list.id < other.subscription_list.id:
            return True
        return self.prio < other.prio


def _get_class(cls_or_obj: Any) -> Type:
    return cls_or_obj if inspect.isclass(cls_or_obj) else cls_or_obj.__class__


class ClassSubscriptionList(SubscriptionList):
    """
    A subscription list based on classes; the fully qualified name
    of a class will be used as id.
    """

    def __init__(self, cls_or_obj: Any, prefix: str = ""):
        cls = _get_class(cls_or_obj)

        super().__init__(f"{prefix}{cls.__module__}.{cls.__qualname__}")

    def __repr__(self) -> str:
        return f"<ClassSubscriptionList class='{self.id}'>"


def get_superclass_subscribers(cls_or_obj, prefix: str = ""):
    """
    Iterate over all classsubscribers of `cls_or_object` and all superclasses in the
    order of __mro__.
    """
    cls = _get_class(cls_or_obj)
    for super_cls in cls.__mro__:
        yield from ClassSubscriptionList(super_cls, prefix).subscribers


def call_superclass_subscribers(cls_or_obj, prefix: str = "", *args, **kwargs):
    """
    Iterate over all classsubscribers of `cls_or_object` and all superclasses in the
    order of __mro__ and call all subscribers.
    """
    cls = _get_class(cls_or_obj)
    for super_cls in cls.__mro__:
        ClassSubscriptionList(super_cls, prefix).call_subscribers(*args, **kwargs)
