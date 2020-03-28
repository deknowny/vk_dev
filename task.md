# Task
* Create useful and comfortable python module to write scripts that works with VK API
* Structed by decorators, like @chat means. that code will be work only in chat, @from_user means code will react only to users

# Examples
```python
from vk_bot import (
        Auth, peer
    )

api, handler = Auth(
        token="token",
        v=5.103,
        group_id=12345
    )

lp = handler.LongPoll()

@subscribed
@direct
@lp.message_new
def hello(event, pl):
    """
    Will answer, if will come new message from user
    that followed to the group
    """

    api.messages.send(
        peer_id=event.object.message.from_id,
        message=f"""
        Hello, how are you?
        I think, your user_id is {event.object.message.from_id}
        """,
        random_id=0
    )

if __name__ == '__main__':
    lp()
```
```python
import vk_bot
from vk_bot import peer

# vk = vk_bot.Auth(token="token", v=5.103)
# lp = vk.LongPoll(group_id=12345)

@lp.message_allow
async def greeting(event, pl):
    await vkapi.messages.send(
        peer_id=peer + 10,
        message="Hey, You're welcome",
        random_id=0
    )
```
```python
import vk_bot

resp = Photo("file.png")
```
