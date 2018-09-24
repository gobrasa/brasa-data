import itertools
import string

def excel_cols():
    """
    Generate list containing excel column names ordered alphabetically.
    Usage: list(itertools.islice(excel_cols(), 28))
    :return:
    """
    n=1
    while True:
        yield from (''.join(group) for group in itertools.product(string.ascii_uppercase, repeat=n))
        n += 1
