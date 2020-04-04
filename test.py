from vk_dev import (
    Auth, Condition, peer
)
import vk_dev
from vk_dev.cond import (
    Prefix, Path
)

import config as conf

api, handler = Auth(
    token=conf.TOKEN,
    v=5.103,
    group_id=192979547
)

lp = handler.LongPoll()

@Prefix('/kb')
@lp.message_new()
def keyboard(event, pl):
    keyboard = {
        'inline': True,
        'buttons': [
            [
                {
                    'action': {
                        'type': 'text',
                        'payload': '{}',
                        'label': 'Some text'
                    },
                    'color': 'positive'
                }
            ]
        ]
    }
    api.messages.send(
        peer_id=447532348,
        message='Your keyboard, sir.',
        keyboard=handler.Keyboard(keyboard),
        random_id=0
    )

@Path('direct')
@Prefix('.')
@lp.message_new(lambda event: event.object.message.text)
def react(event, pl):
    print(event)
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
