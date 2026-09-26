from __future__ import annotations
import threading
_state = threading.local()
def set_filter(value): _state.value = value
def take_filter():
    value = getattr(_state, 'value', None)
    _state.value = None
    return value
