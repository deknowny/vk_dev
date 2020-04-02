from vk_bot import (
    Auth, Condition, peer
)

api, handler = Auth(
    token='d02a9baaf2d510c55a49f0403bbb80eb816aed271de9ae5385f75e3342bbcc77541a9bd22933968d2efa7',
    v=5.103,
    group_id=192979547
)


lp = handler.LongPoll()

class Prefix(Condition):
    """
    Check how message start
    """

    def __init__(self, *prefixes):
        self._prefixes = prefixes

    def code(self, event, pl):
        print(event.object.message.text)

        if event.object.message.text.startswith(self._prefixes):
            return True
        return False

class Path(Condition):
    """
    Path to writiing
    """

    def __init__(self, path):
        self._path = path

    def code(self, event, pl):
        if event.object.message.peer_id < peer:
            return 'direct' == self._path
        else:
            return 'chat' == self._path

@Path('direct')
@Prefix('.')
@lp.message_new(lambda event: event.object.message.text)
def react(event, pl):
    api.messages.send(
        peer_id=447532348,
        message=f'Hello there. You said {pl}',
        random_id=0
    )

@Path('chat')
@Prefix('/')
@lp.message_new()
def ree(event, pl):
    api.messages.send(
        peer_id=447532348,
        message='How are you?',
        random_id=0
    )

if __name__ == '__main__':
    lp()


# some = {'message_new': {
#             'box': [
#                 {
#                     False: {<function ree at 0x7ffdc8098170>},
#                     True: {<function react at 0x7ffdc8071d40>},
#                     'cond': <__main__.Prefix object at 0x7ffdc8097650>
#                 },
#                 {
#                     False: {<function react at 0x7ffdc8071d40>},
#                     True: {<function ree at 0x7ffdc8098170>},
#                     'cond': <__main__.Prefix object at 0x7ffdb80346d0>
#                 }
#             ],
#              'reactions': {
#                     <function react at 0x7ffdc8071d40>,
#                     <function ree at 0x7ffdc8098170>}
#                 }
#         }
