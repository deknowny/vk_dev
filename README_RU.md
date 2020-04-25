# vk_dev
[![PyPI version](https://badge.fury.io/py/vk-dev.svg)](https://badge.fury.io/py/vk-dev)
[![Downloads](https://pepy.tech/badge/vk-dev/week)](https://pepy.tech/project/vk-dev/week)

## Информация
> *Что такое удобство на самом деле?*

Перед вами есть возможность испытать прекрасный пакет для python для разработки под API ВКонтакте. Используя самый сахар python, эта библиотека позволит писать вам код в наиболее читабельном стиле, не усложняя его, когда скорость создания важна ~или горит дедлайн~, и позволяя рефакторить проект макcимально удобно и осмысленно
## Установка
```bash
$ pip3 install vk_dev
```
## Пример
```python
import vk_dev

api = vk_dev.Api(
    token='token',
    group_id=192979547,
    v=5.103
)
lp = api >> vk_dev.LongPoll()

## Можно создать любой свой декоратор
@vk_dev.cond.Path('direct')
@vk_dev.cond.Prefix('/', '.')
@lp.message_new()
async def reaction(event, pl):
    """
    Эта функция сработает, если сообщение
    отправлено в лс и начинается с
    символов `/` или `.`
    """

    ## Отправка ответа пользователю
    await api.messages.send(
        peer_id=event.object.message.peer_id,
        message='Hello there',
        random_id=vk_dev.random_id()
    )

if __name__ == '__main__':
    lp()
```
## Документация
* [Wiki](https://github.com/Rhinik/vk_dev/wiki)
