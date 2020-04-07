import vk_dev

api, handler = vk_dev.Auth(
    token='token',
    group_id=123,
    v=5.103
)
lp = handler.longpoll()


# Можно создать любой свой декоратор
@vk_dev.cond.Path('direct')
@vk_dev.cond.Prefix('/', '.')
@lp.message_new()
async def reaction(event, pl):
    """
    Эта функция сработает, если сообщение
    отправлено в лс и начинается с
    символов `/` или `.`
    """

    # Отправка ответа пользователю
    await api.messages.send(
        peer_id=event.object.message.peer_id,
        message='Hello there',
        random_id=0
    )


if __name__ == '__main__':
    lp()
