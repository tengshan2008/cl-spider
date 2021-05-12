from typing import Text


def bit2humanView(bit_val: int) -> Text:
    kb = bit_val / 1024
    mb = bit_val / 1024 / 1024
    gb = bit_val / 1024 / 1024 / 1024
    if int(gb) is not 0:
        return f'{gb:.2f} GB'
    if int(mb) is not 0:
        return f'{mb:.2f} MB'
    if int(kb) is not 0:
        return f'{kb:.2f} KB'
    return f'{bit_val} bit'
