'''
Magic application base code
'''
from curses import wrapper
import os

from magicur.screen import MagicScreen
from magicur.palette import Palette
import logging
from logging import NullHandler
from magicur.event import HookEvent, KeyEvent
import asyncio
import sys
from threading import Thread
from _curses import ungetch
import queue
import threading


class MagicBootstrap:

    def __init__(self, debug_log_file=None, debug_string=None):
        self._debug_log_file = debug_log_file
        self._debug_string = debug_string

    def _create_null_logger(self):
        log = logging.getLogger("default")
        log.setLevel(logging.INFO)
        log.addHandler(NullHandler())
        return log

    def _create_file_handler(self, log_file):
        formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)s')
        handler = logging.FileHandler(log_file)
        handler.setLevel(logging.DEBUG)
        handler.setFormatter(formatter)
        return handler

    def _inject_logger_factory(self, application):
        if self._debug_log_file is None:
            null_logger = self._create_null_logger()
            application._logger_factory = lambda _: null_logger
        else:
            handler = self._create_file_handler(self._debug_log_file)

            def get_logger(name):
                log = logging.getLogger(name)
                log.setLevel(logging.DEBUG)
                log.addHandler(handler)
                return log

            application._logger_factory = get_logger

    def _start_debugging_if_requested(self):
        if self._debug_string and len(self._debug_string) > 0:
            debug_tuple = self._debug_string.split(":")
            sys.path.append(debug_tuple[2])
            import pydevd
            pydevd.settrace(debug_tuple[0], debug_tuple[1])

    def run(self, application):
        self._inject_logger_factory(application)
        self._start_debugging_if_requested()
        application._terminating = False
        return application.run()


def callback(method):
    """Decorated method won't be called directly but scheduled for execution in 
       application's event-loop"""

    async def scheduled_callback(obj, *args):
        await obj.schedule_hook(method, *(tuple([obj]) + args))

    return scheduled_callback


class ThreadSafeEvent(asyncio.Event):

    def set(self):
        self._loop.call_soon_threadsafe(super().set)


class MagicApplication:
    """Base Application class, initialized by MagicCurses.run() method"""

    def get_logger(self, name):
        return self._logger_factory(name)

    def init_palette(self, palette):
        self._log.debug("Initializing palette")
        palette.add_default_colors()

    def init_view(self, screen):
        self._log.debug(f"Initializing view, width: {screen.width}, height: {screen.height}")

    def on_start(self):
        self._log.debug("Application starting")

    def on_termination(self):
        self._log.debug("Application terminating")

    def on_key(self, key):
        if key == 27:
            self.terminate()

    def on_resize(self, new_width, new_height):
        pass

    def resize(self):
        self.on_resize(self._screen.width, self._screen.height)

    def terminate(self):
        self._log.debug("Terminate called")
        self._terminating = True
        self._kill_getch_loop.set()

    def terminating(self):
        return self._terminating

    def on_error(self, error, task=None):
        if task is None:
            self._log.error(f"Error while handling event {str(error)}")
        else:
            self._log.error(f"Error while executing task {task}: {str(error)}")
        self.terminate()

    @callback
    def on_task_error(self, task, error):
        self.on_error(error, task=task)

    def _initial_events(self):
        return [
            HookEvent(self.init_palette, self._palette),
            HookEvent(self.init_view, self._screen),
            HookEvent(self.on_start)
        ]

    def schedule_async(self, task):
        self._loop.create_task(task)

    async def schedule_hook(self, method, *args):
        await self._event_queue.put(HookEvent(method, *args))

    async def _read_key_events(self):

        # curses getch() method needs to be called in blocking mode
        # because otherwise we'd end up with CPU consuming while loop

        def getch_loop(screen1, queue1, event1):
            while True:
                queue1.put(screen1.getch())
                event1.set()

        getch_loop_queue = queue.Queue()
        getch_loop_event = ThreadSafeEvent()

        # TODO: if there's a way how to interrupt getch() from other thread
        # let's do it, but so far we have to create this thread as a daemon
        # and leave it to be cleaned up on exit
        Thread(
            target=getch_loop,
            name="getch_loop",
            args=(self._screen, getch_loop_queue, getch_loop_event),
            daemon=True).start()

        while not self._terminating:
            await getch_loop_event.wait()
            getch_loop_event.clear()
            emptied = False
            while not emptied:
                try:
                    key = getch_loop_queue.get_nowait()
                    await self._event_queue.put(KeyEvent(key))
                except queue.Empty:
                    emptied = True
                    await asyncio.sleep(0)

        self._log.debug("Finishing key event reader")

    async def _schedule_initial_events(self):
        for event in self._initial_events():
            await self._event_queue.put(event)

    async def _dispatch_events(self):
        while not self._terminating:
            event = await self._event_queue.get()
            try:
                if isinstance(event, KeyEvent):
                    self.on_key(event.key)
                elif isinstance(event, HookEvent):
                    event.method(*(event.args))
                else:
                    raise Exception("unknown event type")
            except Exception as e:
                self.on_error(e)
        self._log.debug("Finishing event dispatcher")

    async def _run_async(self):
        self._kill_getch_loop = asyncio.Event()
        self._event_queue = asyncio.Queue()
        try:
            await asyncio.gather(
                self._schedule_initial_events(),
                self._read_key_events(),
                self._dispatch_events())
        finally:
            self._log.debug(f"Event queue {repr(self._event_queue)}")
            self.on_termination()
            self._log.debug(f"Event loop terminated")

    def _run_in_curses(self, stdscr):
        self._screen = MagicScreen(stdscr, self._log, self)
        self._palette = Palette.instance()
        self._loop = asyncio.get_event_loop()
        try:
            self._loop.run_until_complete(self._run_async())
        finally:
            self._loop.close()

    def run(self):
        self._log = self.get_logger("app")
        os.environ.setdefault('ESCDELAY', '25')
        try:
            wrapper(self._run_in_curses)
            return 0
        except KeyboardInterrupt as e:
            self._log.debug("Keyboard interrupt")
            return 0
        except Exception as e:
            self._log.error("An unhandled error occured", exc_info=True)
            print("ERROR: {0}".format(e))
            return 1

