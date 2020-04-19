from random import randint

peer = int(2e9)


def random_id(between: int = 2147483647):
    """
    Return random_id for
    messages.send method
    """
    return randint(-between, between)
