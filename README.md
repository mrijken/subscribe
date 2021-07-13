# Subscribe

A simple yet powerfull subscription library in Python for managing subscriptions.

## Concepts

Every subscription consists of

- *subscription_list* - a unique identification (just a string) for a list to which is subscribed
- *prio* - a integer with the prio of the subscription which will be used to order the subscriptions
  (from low to high)
- *subscriber* - The object which is subscribed. Can be anything. Often a callable,.

`subscribe` is very flexible and may require some boilerplate to setup. For some frequent use cases
we have made helpers: `Event` and `Command`. These are simply to use, so we will the tutorial with
these.


## Quick start

   Import subscribe

    >>> import subscribe

### Event

    An Event is a class whose instance can be used to notify handler, which will
    receive the event as single argument.

    Create an Event

    >>> class UserCreated(subscribe.Event):
    ...     def __init__(self, name: str):
    ...         self.name = name
    ...         self.notify()

    >>> called_handlers = []

    Add some subscribers

    >>> @UserCreated.subscribe
    ... def send_mail(event: UserCreated):
    ...     called_handlers.append(f"Send email to {event.name}")

    >>> @UserCreated.subscribe
    ... def add_default_groups(event: UserCreated):
    ...     called_handlers.append(f"Add default groups {event.name}")

    Instantiate the event (and call the handlers, because the `__init__`
    method calls the `notify` method).

    >>> user_created = UserCreated("marc")

    >>> called_handlers
    ['Send email to marc', 'Add default groups marc']


### Command

    A command is special kind of event, with the following differences:
    - A command must have exactly 1 handler
    - The command will return the return value of the handler

    Create a Command

    >>> class SendEmail(subscribe.Command):
    ...     def __init__(self, message: str):
    ...         self.message = message

    >>> called_handlers = []

    Add a subscriber

    >>> @SendEmail.subscribe
    ... def send_mail(event: SendEmail, email: str):
    ...     called_handlers.append(f"Send email to {email}")
    ...     return email

    >>> user_created = SendEmail("Welcome")
    >>> user_created.execute(email="marc@rijken.org")
    'marc@rijken.org'

    >>> user_created.execute(email="john@example.com")
    'john@example.com'

    >>> called_handlers
    ['Send email to marc@rijken.org', 'Send email to john@example.com']

## Flexible subscriptions

`Event` and `Command` are two predefined use cases of subscriptions. You
can define your own to get more flexibility, both in defining the subscribers
and subscriptions as calling the subcriptions.

### SubscriptionList

    Subscriptions are collected in a `SubscriptionList` which is identified by a
    string. It is easy to create one.

    >>> new_user = subscribe.SubscriptionList("new_user")

### Subscribe to the SubscriptionList

    You can add a subscriber by using the `subscribe` decorator of the
    SubscriptionList.

    >>> @new_user.subscribe()
    ... def send_mail(user):
    ...     pass

    The subscribers can be anything, so they do not have to be callables.

    You can subscribe multiple subscribers to the same SubscriptionList.
    The subscribers will be sorted in order of priority. When no priority is given, the priority
    will be equal to 0 and the subscriptions will be in order of addition.

    >>> @new_user.subscribe(priority=-1)
    ... def compute_age(user):
    ...     pass


### Get the subscriptions

    You can get the subscriptions (which contains the subscriber, subscription list and priortiy), 
    ie so you call the subscribed functions. Of course you can not call the subscribers if 
    they are not callable, but you
    can iterate over them to do whatever you want.

    >>> [i for i in new_user.get_subscriptions()]
    [Subscription(subscription_list=<SubscriptionList id='new_user'>, priority=-1, subscriber=<function compute_age at ...>), Subscription(subscription_list=<SubscriptionList id='new_user'>, priority=0, subscriber=<function send_mail at ...>)]

    Or just the subscribers, which is most of the time what you want

    >>> [i.__name__ for i in new_user.get_subscribers()]
    ['compute_age', 'send_mail']

    You can also use the `subscribers` property.

    >>> [i.__name__ for i in new_user.subscribers]
    ['compute_age', 'send_mail']

    Often the subscribers are callables. You can call them all with
    the same parameters. Note: return value will not be collected and returned
    
    >>> new_user.call_subscribers(user="marc")


### Advanced Usage

#### Class based SubscriptionList

    An important use case is to subscribe to classes, which
    will use the fully qualified name of the class as the
    SubscriptionLIst identification.

    >>> class EventBase:
    ...   pass
    >>> class NewUserEvent(EventBase):
    ...   pass

    >>> new_user_event = subscribe.ClassSubscriptionList(NewUserEvent)
    >>> new_user_event
    <ClassSubscriptionList class='__main__.NewUserEvent'>

    You do not have to pass the subscription list around; you can
    recreate it:

    >>> new_user_event == subscribe.ClassSubscriptionList(NewUserEvent)
    True

    And use it as a regular SubscriptionList to subscribe.

    >>> @new_user_event.subscribe()
    ... def subscriber1():
    ...     pass
    >>> @new_user_event.subscribe()
    ... def subscriber2():
    ...     pass

    And get the subscribers as a regular SubscriptionList.

    >>> list(new_user_event.get_subscribers()) == [subscriber1, subscriber2]
    True
    >>> list(new_user_event.subscribers) == [subscriber1, subscriber2]
    True

    If you do not have the instance of the SubscriptionList anymore, you can
    get a new one by passing the class or the instance to ClassSubscriptionList.

    >>> list(subscribe.ClassSubscriptionList(NewUserEvent).subscribers) == [subscriber1, subscriber2]
    True

    >>> list(subscribe.ClassSubscriptionList(NewUserEvent()).subscribers) == [subscriber1, subscriber2]
    True

### Superclass

    ClassSubscriptionList will iterate over the subscribers for the exact same class. If you want to
    use the superclass to iterate over all it subscribers and the subscribers of it's subclasses,
    you have to use SuperClassSubscriptionList

    >>> super_new_user_event = subscribe.SuperClassSubscriptionList(NewUserEvent)
    >>> base_event = subscribe.SuperClassSubscriptionList(EventBase)

    The subclass still has the same subscribers

    >>> list(super_new_user_event.subscribers) == [subscriber1, subscriber2]
    True

    When we create a subscriber on the superclass

    >>> @base_event.subscribe()
    ... def event_subscriber():
    ...     pass

    that will be visible as subscriber on the subclass.

    >>> list(super_new_user_event.subscribers) == [subscriber1, subscriber2, event_subscriber]
    True

    And on the superclass

    >>> list(base_event.subscribers) == [event_subscriber]
    True

#### Prefix on names

    The class name will be used for the identification. So if you want to create
    different SubscriptionLists for the same class, you can add a prefix to the
    SubscriptionList:

    When a prefix is used, `partial` can be used to make sure the right prefix is used every time.
    
    >>> prefixed_new_user_event = subscribe.ClassSubscriptionList(NewUserEvent, prefix='my_prefix')
    >>> prefixed_new_user_event == new_user_event
    False

    You can use partial to make sure that you uses the same prefix.

    >>> import functools
    >>> PrefixedClassSubscriptionList = functools.partial(subscribe.ClassSubscriptionList, prefix='my_prefix')
    >>> prefixed_new_user_event = PrefixedClassSubscriptionList(NewUserEvent)
    >>> @prefixed_new_user_event.subscribe()
    ... def subscriber5():
    ...     pass
    >>> list(prefixed_new_user_event.subscribers) == [subscriber5]
    True



#### Multiple instantiation

    A subscription list can be created multiple times

    >>> first = subscribe.SubscriptionList("my list")
    >>> second = subscribe.SubscriptionList("my list")

    Both can be used to subscribe.

    >>> first.subscribe()("subscribe to first")
    'subscribe to first'
    >>> second.subscribe()("subscribe to second")
    'subscribe to second'

    Both will have the same subscriptions.

    >>> [i.subscriber for i in first.get_subscriptions()]
    ['subscribe to first', 'subscribe to second']
    >>> [i.subscriber for i in second.get_subscriptions()]
    ['subscribe to first', 'subscribe to second']
    
#### Subclass SubscriptionList

    You can subclass SubscriptionList, like we did with ClassSubscriptionList.

    For example, if you have users.

    >>> class User:
    ...     def __init__(self, username):
    ...         self.username = username

    Which could be used to subscribe to, like subscribing to Twitter accounts

    >>> class UserSubscriptionList(subscribe.SubscriptionList):
    ...     def __init__(self, user: User):
    ...         super().__init__(f"user:{user.username}")

    Note: the subscription list is in memory and not persistent. You can implement your own 
    persistency for your SubscriptionList subclass when appropriate.