# Subscribe

A simple yet powerfull subscription library in Python for managing subscriptions.

## Concepts

Every subscription consists of

- *subscription_list* - a unique identification (just a string) for a list to which is subscribed
- *prio* - a integer with the prio of the subscription which will be used to order the subscriptions
  (from low to high)
- *subscriber* - The object which is subscribed. Can be anything. Often a function.


## Quick start

   Import subscribe

    >>> import subscribe

### Create a SubscriptionList

    Make a subscription list

    >>> new_user = subscribe.SubscriptionList("new_user")

### Subscribe to the subscription_list

    Add a first subscriber, ie a function.

    >>> @new_user.subscribe()
    ... def send_mail(user):
    ...     pass

### Get the subscriptions

    Get the subscriptions, ie so you call the subscribed functions.

    >>> [i for i in new_user.get_subscriptions()]
    [Subscription(subscription_list=<SubscriptionList id='new_user'>, prio=0, subscriber=<function send_mail at ...>)]

    Or just the subscribers, which is most of the time what you want

    >>> [i.__name__ for i in new_user.get_subscribers()]
    ['send_mail']

    You can also use the `subscribers` property.

    >>> [i.__name__ for i in new_user.subscribers]
    ['send_mail']

    Often the subscribers are callables. You can call them all with
    same parameters.
    
    >>> new_user.call_subscribers(user="marc")

### Priority

    You can subscribe multiple times to the same SubscriptionList.
    The subscriptions will be sorted in order of prio. When no prio is given, the prio
    will be equal to 0 and the subscriptions will be in order of addition.

    >>> @new_user.subscribe(prio=-1)
    ... def compute_age(user):
    ...     pass

    Get the subscribers.

    >>> [i.__name__ for i in new_user.get_subscribers()]
    ['compute_age', 'send_mail']

    You can subscribe anything, not just functions. It is up to you.  
    Ie it can be a string.

    >>> sentence = subscribe.SubscriptionList("sentence")

    >>> word = sentence.subscribe()("Python")
    >>> word = sentence.subscribe()("is")
    >>> word = sentence.subscribe(prio=5)("language")
    >>> word = sentence.subscribe(prio=2)("nice")
    >>> word = sentence.subscribe(prio=1)("a")

    And you can get the strings in the order of the prio.

    >>> ' '.join(sentence.get_subscribers())
    'Python is a nice language'

### Advanced Usage

#### Class based SubscriptionList

    An important use case is to subscribe to classes. Ie if
    you have a class NewUserEvent

    >>> class Event:
    ...     pass
    >>> class NewUserEvent(Event):
    ...   pass

    You can create a class subscription, which will convert the class into
    a subscription list with the fully qualified name as id.

    >>> new_user_event = subscribe.ClassSubscriptionList(NewUserEvent)
    >>> new_user_event
    <ClassSubscriptionList class='__main__.NewUserEvent'>

    >>> @new_user_event.subscribe()
    ... def subscriber1():
    ...     pass
    >>> @new_user_event.subscribe()
    ... def subscriber2():
    ...     pass

    You can get the subscribers

    >>> list(new_user_event.get_subscribers()) == [subscriber1, subscriber2]
    True
    >>> list(new_user_event.subscribers) == [subscriber1, subscriber2]
    True

    An instance of the class can also be used to get the subscription list also, so
    you do not have to carry the subscription list instance throughout your app.

    >>> list(subscribe.ClassSubscriptionList(NewUserEvent()).subscribers) == [subscriber1, subscriber2]
    True

    A class can have superclasses for which subscription lists are defined also.

    >>> event = subscribe.ClassSubscriptionList(Event)
    >>> @event.subscribe()
    ... def event_subscriber():
    ...     pass

    The ClassSubscriptionList will not iterate over the subscribers of the superclasses, just
    over the subscribers of the class. 

    >>> list(new_user_event.subscribers) == [subscriber1, subscriber2]
    True

    If you want to iterate over the subscriber of the superclasses also, you can use SuperClassSubscriptionList.

    >>> super_new_user_event = subscribe.SuperClassSubscriptionList(NewUserEvent)
    >>> super_event = subscribe.SuperClassSubscriptionList(Event)

    Both SuperClassSubscriptionList and ClassSubscriptionList convert the class to the same string 
    (the dotted name of the class) which is used for the lookup. So an instance of SuperClassSubscriptionList can also 
    find the subscribers of ClassSubscriptionList.

    >>> list(super_new_user_event.subscribers)  == [subscriber1, subscriber2, event_subscriber]
    True
    >>> list(super_event.subscribers) == [event_subscriber]
    True

    When a prefix is used, `partial` can be used to make sure the right prefix is used every time.

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