# vk_dev
Localizations:
* [README on Russian](./README_RU.md)

## Info
> *What true convenience is?*

You have a lot of *doorways* to try amazing python package for developing with API VKontakte. By using the flavor of python this library let you write on readable style without complications when need write fast ~or when you are at 0 days~ and refactor your project conveniencly and with idea.

## Installation
```bash
pip3 install vk_dev
```
## Example
```python
import vk_dev

api, handler = vk_dev.Auth(
    token='token',
    group_id=192979547,
    v=5.103
)
lp = handler.LongPoll()

## You can create own decorators
@vk_dev.cond.Path('direct')
@vk_dev.cond.Prefix('/', '.')
@lp.message_new()
def reaction(event, pl):
    """
    This function will work if
    message was sended to direct and
    starts at `/` or `.`
    """

    ## Send response to the interlocutor
    api.messages.send(
        peer_id=event.object.message.peer_id,
        message='Hello there',
        random_id=vk_dev.random_id()
    )

if __name__ == '__main__':
    lp()
```
## Documentation
* [Wiki](https://github.com/Rhinik/vk_dev/wiki)
