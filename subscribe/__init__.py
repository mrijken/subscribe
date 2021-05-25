import dataclasses
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
        if not isinstance(other, self.__class__):
            return True
        if self.subscription_list.id < other.subscription_list.id:
            return True
        return self.prio < other.prio


class ClassSubscriptionList(SubscriptionList):
    """
    A subscription list based on classes; the fully qualified name
    of a class will be used as id.
    """

    def __init__(self, cls: Type, prefix: str = ""):
        super().__init__(f"{prefix}{cls.__module__}.{cls.__qualname__}")

    def __repr__(self) -> str:
        return f"<ClassSubscriptionList class='{self.id}'>"
