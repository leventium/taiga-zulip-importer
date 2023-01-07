"""
File with user exceptions.
"""


class EmptyConfigField(Exception):
    """
    Exception for case when user forgot to fill some field in config.
    """
    pass
