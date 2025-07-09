# Copyright (c) 2025 JoeBlakeB
# All Rights Reserved

import sys

def print_flush(*args, **kwargs):
    """
    Print to stdout and flush immediately.
    """
    print(*args, **kwargs)
    sys.stdout.flush()
