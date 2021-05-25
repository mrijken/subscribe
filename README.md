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

    >>> ' '.join([i for i in sentence.get_subscribers()])
    'Python is a nice language'

### Advanced Usage

#### Class based SubscriptionList

    An important use case is to subscribe to classes. Ie if
    you have a class NewUserEvent

    >>> class NewUserEvent:
    ...   pass

    You can create a class subscription, which will convert the class into
    a subscription list with the fully qualified name as id.

    >>> new_user_event = subscribe.ClassSubscriptionList(NewUserEvent)
    >>> new_user_event
    <ClassSubscriptionList class='__main__.NewUserEvent'>

    >>> new_user_event.subscribe()("1")
    '1'
    >>> new_user_event.subscribe()("2")
    '2'
    >>> [i for i in new_user_event.get_subscribers()]
    ['1', '2']

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

    You can subclass SubscriptionList, like we did for ClassSubscriptionList.

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