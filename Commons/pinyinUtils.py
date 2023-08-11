import pinyin


def getFullName(name) -> str:
    """
    Parse Chinese name into Pinyin with format "Zhang Zhong jie"

    Args:
        name: name in Chinese
    Returns:
        name in pinyin
    """
    fullname = pinyin.get(name, delimiter=" ", format="strip")
    return fullname
