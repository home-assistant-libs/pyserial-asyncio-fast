#!/usr/bin/env python
#
# This file is part of pySerial-asyncio - Cross platform serial port support for Python
# (C) 2016 pySerial-team
#
# SPDX-License-Identifier:    BSD-3-Clause
"""\
Test asyncio related functionality.

To run from the command line with a specific port with a loop-back,
device connected, use:

  $ cd pyserial-asyncio
  $ python -m test.test_asyncio SERIALDEVICE

"""

import os
import subprocess
import unittest
import asyncio
from typing import Optional

import serial_asyncio_fast

HOST = "127.0.0.1"
_PORT = 8888

# on which port should the tests be performed:
PORT = "socket://%s:%s" % (HOST, _PORT)


@unittest.skipIf(os.name != "posix", "asyncio not supported on platform")
class Test_asyncio(unittest.TestCase):
    """Test asyncio related functionality"""

    def setUp(self):
        self.loop = asyncio.new_event_loop()
        # create a closed serial port

    def tearDown(self):
        self.loop.close()

    def test_asyncio(self):
        TEXT = b"Hello, World!"
        COUNT = 1024
        COMPLETE_MESSAGE = TEXT * COUNT + b"\n"
        received = []
        actions = []
        done = asyncio.Event()

        class Input(asyncio.Protocol):
            def __init__(self):
                super().__init__()
                self._transport = None

            def connection_made(self, transport: serial_asyncio_fast.SerialTransport):
                self._transport = transport

            def data_received(self, data):
                self._transport.write(data)

        class Output(asyncio.Protocol):
            def __init__(self):
                super().__init__()
                self._transport: Optional[serial_asyncio_fast.SerialTransport] = None

            def connection_made(self, transport: serial_asyncio_fast.SerialTransport):
                self._transport = transport
                actions.append("open")
                for _ in range(COUNT):
                    transport.write(TEXT)
                transport.write(b"\n")

            def data_received(self, data):
                received.append(data)
                if b"\n" in data:
                    self._transport.close()

            def connection_lost(self, exc):
                actions.append("close")
                done.set()

            def pause_writing(self):
                actions.append("pause")
                print(self._transport.get_write_buffer_size())

            def resume_writing(self):
                actions.append("resume")
                print(self._transport.get_write_buffer_size())

        if PORT.startswith("socket://"):
            coro = self.loop.create_server(Input, HOST, _PORT)
            self.loop.run_until_complete(coro)

        client = serial_asyncio_fast.create_serial_connection(self.loop, Output, PORT)
        self.loop.run_until_complete(client)
        self.loop.run_until_complete(done.wait())
        pending = asyncio.all_tasks(self.loop)

        async def gather_pending():
            await asyncio.gather(*pending)

        self.loop.run_until_complete(gather_pending())

        for _ in range(1024):
            self.loop.run_until_complete(asyncio.sleep(0))
        
        all_data = b"".join(received)
        self.assertEqual(all_data, COMPLETE_MESSAGE)
        self.assertEqual(actions, ["open", "close"])

class AsyncTests(unittest.IsolatedAsyncioTestCase):
    async def test_remove_writer(self) -> None:
        TEXT = b"Hello, World!"
        COUNT = 8 * 1024

        IN_TTY = "/tmp/ttyTestIn"
        OUT_TTY = "/tmp/ttyTestOut"

        # Use socat to create a pair of linked PTYs to simulate two connected
        # serial ports.
        socat = subprocess.Popen(
            ["socat", f"pty,link={IN_TTY},raw,echo=0", f"pty,link={OUT_TTY},raw,echo=0"]
        )

        # Give socat some time to set up the PTYs.
        await asyncio.sleep(0.5)
        self.assertIsNone(socat.poll(), "socat process exited unexpectedly")

        output_resume_event = asyncio.Event()

        class Input(asyncio.Protocol):
            """
            Echoes back whatever data it receives.
            """
            def connection_made(self, transport: asyncio.BaseTransport) -> None:
                assert isinstance(transport, serial_asyncio_fast.SerialTransport)
                self._transport = transport

            def data_received(self, data: bytes) -> None:
                self._transport.write(data)

        class Output(asyncio.Protocol):
            """
            Provides backpressure to writer via output_resume_event.
            """
            def connection_made(self, transport: asyncio.BaseTransport) -> None:
                assert isinstance(transport, serial_asyncio_fast.SerialTransport)
                self._transport = transport
                output_resume_event.set()

            def pause_writing(self) -> None:
                output_resume_event.clear()

            def resume_writing(self) -> None:
                output_resume_event.set()

        loop = asyncio.get_running_loop()

        in_transport, _ = await serial_asyncio_fast.create_serial_connection(loop, Input, IN_TTY)
        out_transport, _ = await serial_asyncio_fast.create_serial_connection(loop, Output, OUT_TTY)

        # Write a bunch of data so that we create a buffer and a writer.
        for _ in range(COUNT):
            await asyncio.wait_for(output_resume_event.wait(), timeout=5)
            out_transport.write(TEXT)

        # Ensure that we actually sent enough data to have a writer added to
        # the event loop.
        self.assertTrue(out_transport._has_writer)

        # Then make sure that the writer is removed when the buffer is drained.
        async def poll_has_writer() -> None:
            while out_transport._has_writer:
                await asyncio.sleep(0.1)

        await asyncio.wait_for(poll_has_writer(), timeout=5)

        out_transport.close()
        in_transport.close()
        socat.terminate()


if __name__ == "__main__":
    import sys

    sys.stdout.write(__doc__)
    if len(sys.argv) > 1:
        PORT = sys.argv[1]
    sys.stdout.write("Testing port: %r\n" % PORT)
    sys.argv[1:] = ["-v"]
    # When this module is executed from the command-line, it runs all its tests
    unittest.main()
