# Special kind of subscriptions with some convenience methods for Events

import inspect
from typing import Any, Callable, Dict

from subscribe.subscriptions import ClassSubscriptionList


class EventBase:
    @classmethod
    def _get_subscription_list(cls):
        return ClassSubscriptionList(cls)

    @classmethod
    def subscribe(cls, f=None):
        return cls._get_subscription_list().subscribe(f=f)

    @classmethod
    def inject_dependencies(cls, **dependencies: Dict[str, Any]):
        """
        Injects the `dependencies` into the subscribers. All `dependencies`
        are passed as keyword arguments of the subscriber.

        >>> class Echo(Event):
        ...    pass

        >>> @Echo.subscribe
        ... def echo(event: Echo, print_statement: Callable[[str], None]):
        ...     print_statement(event.__class__.__name__)

        >>> printed_lines = []
        >>> def print_statement(line):
        ...     printed_lines.append(line)

        >>> Echo.inject_dependencies(print_statement = print_statement)

        >>> Echo().notify()

        >>> printed_lines
        ['Echo']

        """
        cls._get_subscription_list().inject_dependencies(**dependencies)


class Event(EventBase):
    """

    >>> class ProductSold(Event):
    ...     number_of_items = 1

    >>> printed_lines = []

    >>> @ProductSold.subscribe
    ... def print_product_sold(event: ProductSold):
    ...     printed_lines.append(f"{event.number_of_items} product(s) sold")

    >>> @ProductSold.subscribe
    ... def reduce_inventory(event: ProductSold):
    ...     printed_lines.append(f"reduce inventory with {event.number_of_items} product(s)")

    >>> ProductSold().notify()
    >>> printed_lines
    ['1 product(s) sold', 'reduce inventory with 1 product(s)']
    """

    def notify(self, **kwargs):
        """
        Call all subscribers of this event with this event as argument and the optional extra arguments (which
        were injected via `inject_dependencies`).
        """
        self._get_subscription_list().call_subscribers(event=self, **kwargs)


class Command(EventBase):
    """A Command is an event which must have exactly 1 subscriber and
    its result will be returned.

    >>> class Echo4(Command):
    ...     def __init__(self, text: str):
    ...         self.text = text

    >>> @Echo4.subscribe
    ... def echo(cmd: Echo4):
    ...     return cmd.text

    >>> Echo4("hello").execute()
    'hello'

    >>> @Echo4.subscribe
    ... def echo2(cmd: Echo4):
    ...     return cmd.x
    Traceback (most recent call last):
    ...
    ValueError: A command may not have more than one handler
    """

    def execute(self, **kwargs):
        """
        Call the command handler with the command as argument and the optional extra arguments (which
        were injected via `inject_dependencies`).

        The return value of the handler is returned.

        >>> class Echo3(Command):
        ...    pass

        >>> printed_lines = []
        >>> def print_statement(line):
        ...     printed_lines.append(line)

        >>> @Echo3.subscribe
        ... def echo(cmd: Echo3, print_statement: Callable[[str], None]):
        ...     return cmd.__class__.__name__

        >>> Echo3().execute(print_statement=print_statement) == 'Echo3'
        True
        """
        subscribers = list(self._get_subscription_list().subscribers)
        if len(subscribers) != 1:
            raise ValueError("A Command must have exactly one handler. It has zero handlers")

        return subscribers[0](self, **kwargs)

    @classmethod
    def subscribe(cls, f=None):
        """
        Set the handler for the command

        >>> class Echo2(Command):
        ...    pass

        >>> @Echo2.subscribe
        ... def echo(cmd: Echo2):
        ...     pass

        """
        if len(list(cls._get_subscription_list().subscribers)) >= 1:
            raise ValueError("A command may not have more than one handler")

        return super().subscribe(f)
