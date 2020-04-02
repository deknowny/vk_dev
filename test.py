from vk_bot import (
    Auth, Condition
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
    # max_values = 0
    # true_one_time = True

    def __call__(self, *prefixes):
        self._prefixes = prefixes
        self._call_switch()

        return self

    def code(self, event, pl):
        if event.object.message.text.startswith(self._prefixes):
            return True
        return False



prefix = Prefix()

@prefix('/')
@lp.message_new()
def react(event, pl):
    api.messages.send(
        peer_id=447532348,
        message='Hello there',
        random_id=0
    )

@prefix('.')
@lp.message_new()
def ree(event, pl):
    api.messages.send(
        peer_id=447532348,
        message='How are you?',
        random_id=0
    )

if __name__ == '__main__':
    lp()
