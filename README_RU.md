# vk_dev
> *Что такое удобство на самом деле?*

Перед вами есть возможность испытать прекрасный пакет для python для разработки под API ВКонтакте. Используя самый сахар python, эта библиотека позволит писать вам код в наиболее читабельном стиле, не усложняя его, когда скорость создания важна ~или горит дедлайн~, и позволяя рефакторить проект макимально удобно и осмысленно
## Установка
```bash
$ pip3 install vk_dev
```
## Пример
```python
import vk_dev

api, handler = vk_dev.Auth(
    token='token',
    group_id=1234567890,
    v=5.103
)
lp = handler.LongPoll()

## Можно создать любой свой декоратор
@vk_dev.cond.Path('direct')
@vk_dev.cond.Prefix('/', '.')
@lp.message_new()
def reaction(event, pl):
    """
    Эта функция сработает, если сообщение
    отправлено в лс и начинается с
    символов `/` или `.`
    """

    ## Отправка ответа пользователю
    api.messages.send(
        peer_id=event.object.message.peer_id,
        message='Hello there',
        random_id=vk_dev.random_id()
    )

if __name__ == '__main__':
    lp()

```
## Документация
* Wiki *(will be added later)*
