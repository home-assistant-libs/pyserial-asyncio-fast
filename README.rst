========================================
 pyserial-asyncio-fast |docs| |codecov|
========================================

Async I/O extension package for the Python Serial Port Extension for OSX, Linux, BSD

It depends on pySerial and is compatible with Python 3.5 and later.

This version implements eager writes like cpython `asyncio` selector_events does:
https://github.com/python/cpython/blob/b89b838ebc817e5fbffad1ad8e1a85aa2d9f3113/Lib/asyncio/selector_events.py#L1063

This can significantly reduce overhead since the asyncio writer is no longer added and removed frequently.

Documentation
=============

- Documentation: http://pyserial-asyncio.readthedocs.io/en/latest/
- Download Page: https://pypi.python.org/pypi/pyserial-asyncio-fast
- Project Homepage: https://github.com/home-assistant-libs/pyserial-asyncio-fast


.. |docs| image:: https://readthedocs.org/projects/pyserial-asyncio/badge/?version=latest
   :target: http://pyserial-asyncio.readthedocs.io/
   :alt: Documentation

.. |codecov| image:: https://codecov.io/gh/home-assistant-libs/pyserial-asyncio-fast/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/home-assistant-libs/pyserial-asyncio-fast