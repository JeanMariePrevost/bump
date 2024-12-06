from queue import Empty, LifoQueue
from enum import Enum, auto
from custom_logging import general_logger


class QueueEvents(Enum):
    """
    Messages that can be sent to the threads queues.
    """

    OPEN_GUI = auto()
    EXIT_APP = auto()
    NO_EVENT = auto()  # E.g. it timed out and was still empty


class SimpleQueue:
    """
    Simply wraps a 1-slot queue for now, with "put" always replacing the previous payload.
    Queue object to provide a blocking put and get method.
    """

    def __init__(self) -> None:
        self.__queue = LifoQueue(maxsize=1)
        pass

    def put_nowait(self, event: QueueEvents) -> None:
        """
        Put a payload into the queue.
        """
        if not isinstance(event, QueueEvents):
            general_logger.error(f"Invalid payload {event}. Expected types: {QueueEvents}")
            raise TypeError(f"Invalid payload {event}. Expected types: {QueueEvents}")
        if self.__queue.full():
            # Log as debug, then empty the queue and put the new event. SimpleQueue only keeps the latest event
            self.__queue.get()
        self.__queue.put_nowait(event)

    def put(self, event: QueueEvents, timeout_s: float = None) -> None:
        """
        Put a payload into the queue.
        """
        if not isinstance(event, QueueEvents):
            general_logger.error(f"Invalid payload {event}. Expected types: {QueueEvents}")
            raise TypeError(f"Invalid payload {event}. Expected types: {QueueEvents}")
        if self.__queue.full():
            # Log as debug, then empty the queue and put the new event. SimpleQueue only keeps the latest event
            self.__queue.get()
        self.__queue.put(item=event, block=True, timeout=timeout_s)

    def get(self, timeout_s: float = None) -> QueueEvents:
        """
        Get a payload from the queue. Caller blocks until a payload is available.
        """
        try:
            return self.__queue.get(block=True, timeout=timeout_s)
        except Empty:
            # Timeout and no events were received
            return QueueEvents.NO_EVENT
        except Exception as e:
            general_logger.error(f"Queue get failed: {e}")
            return QueueEvents.NO_EVENT
