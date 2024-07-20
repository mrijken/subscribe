import warnings

warnings.warn("This package is not maintained anymore", DeprecationWarning)

from subscribe.subscribers import Command, Event  # noqa
from subscribe.subscriptions import (  # noqa
    ClassSubscriptionList,
    Subscription,
    SubscriptionList,
    SuperClassSubscriptionList,
)
