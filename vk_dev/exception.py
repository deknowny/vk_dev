class VkErr(Exception):
    """
    Errors from response from vk
    """
    def __init__(self, text):
        self.text = text
