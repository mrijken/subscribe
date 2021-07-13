import collections
import dataclasses
import functools
import inspect
from typing import Any, Dict, Iterator, List


class SubscriptionList:
    """A list of Subscriptions. The object to which a `subscriber` can `subscribe`"""

    _subscriptions: Dict[str, List["Subscription"]] = collections.defaultdict(list)

    def __init__(self, id_: str):
        self.id = id_

    def __eq__(self, other):
        return self.__class__ == other.__class__ and self.id == other.id

    def subscribe(self, f=None, priority: int = 0):
        """
        Return a decorator to let a subscriber (the decorated object) subscribe
        to a subscription list (self).
        """

        def decorator(decorated_function):
            self._subscriptions[self.id].append(
                Subscription(
                    priority=priority,
                    subscription_list=self,
                    subscriber=decorated_function,
                )
            )
            self._subscriptions[self.id].sort()
            return decorated_function

        if f is None:
            return decorator

        return decorator(f)

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

    def inject_dependencies(self, **dependencies: Dict[str, Any]):
        """
        Replace (when present) the arguments of the subscribers with the arguments in `dependencies`.

        Note: do this only after all subscribers have been subscribed.
        """
        _new_subscriptions = []
        for subscription in self.get_subscriptions():
            subscriber = subscription.subscriber
            if callable(subscriber):
                subscriber_params = inspect.signature(subscriber).parameters
                subscriber_dependencies = {
                    name: dependency for name, dependency in dependencies.items() if name in subscriber_params
                }
                if subscriber_dependencies:
                    subscriber = functools.partial(subscriber, **subscriber_dependencies)

            _new_subscriptions.append(
                Subscription(
                    priority=subscription.priority,
                    subscription_list=subscription.subscription_list,
                    subscriber=subscriber,
                )
            )

        self._subscriptions[self.id] = _new_subscriptions

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
        for subscriber in self.get_subscribers():
            subscriber(*args, **kwargs)

    def __repr__(self) -> str:
        return f"<SubscriptionList id='{self.id}'>"


@dataclasses.dataclass(frozen=True)
class Subscription:
    """
    A single subscription by a `subscriber` to a `subscription_list`
    """

    subscription_list: SubscriptionList
    priority: int
    subscriber: Any

    def __lt__(self, other):
        """
        >>> sl1 = SubscriptionList("1")
        >>> sl2 = SubscriptionList("2")
        >>> Subscription(subscription_list=sl1, priority=1, subscriber=None) < Subscription(subscription_list=sl1, priority=2, subscriber=None)
        True
        >>> Subscription(subscription_list=sl1, priority=2, subscriber=None) < Subscription(subscription_list=sl1, priority=1, subscriber=None)
        False
        >>> Subscription(subscription_list=sl1, priority=1, subscriber=None) < Subscription(subscription_list=sl2, priority=1, subscriber=None)
        True
        >>> Subscription(subscription_list=sl2, priority=1, subscriber=None) < Subscription(subscription_list=sl1, priority=1, subscriber=None)
        False
        >>> Subscription(subscription_list=sl2, priority=1, subscriber=None) < None
        True
        """
        if not isinstance(other, self.__class__):
            return True
        if self.subscription_list.id < other.subscription_list.id:
            return True
        return self.priority < other.priority


class ClassSubscriptionList(SubscriptionList):
    """
    A subscription list based on classes; the fully qualified name
    of a class will be used as id.
    """

    def __init__(self, cls_or_obj: Any, prefix: str = ""):
        self.cls = cls_or_obj if inspect.isclass(cls_or_obj) else cls_or_obj.__class__
        self.prefix = prefix

        super().__init__(f"{self.prefix}{self.cls.__module__}.{self.cls.__qualname__}")

    def __repr__(self) -> str:
        return f"<ClassSubscriptionList class='{self.id}'>"


class SuperClassSubscriptionList(ClassSubscriptionList):
    def get_subscribers(self):
        """
        Iterate over all classsubscribers of self.cls and all superclasses in the
        order of __mro__.
        """
        for super_cls in self.cls.__mro__:
            yield from ClassSubscriptionList(super_cls, self.prefix).subscribers
