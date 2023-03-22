import multiprocessing
from abc import ABC, abstractmethod
from dataclasses import dataclass
from queue import Empty
from typing import Any, Optional


@dataclass
class HashParameter:
    target: bytes
    possible: bytes
    salt: Optional[bytes] = None
    kwargs: Optional[dict[str, Any]] = None


class CrackManager(ABC):
    def __init__(self, queue: multiprocessing.Queue, found: multiprocessing.Event):
        self.queue = queue
        self.found = found
        self.process = multiprocessing.Process(target=self.run, daemon=True)

    def start(self) -> None:
        self.process.start()
        return self

    def stop(self) -> None:
        self.process.terminate()

    def join(self) -> None:
        self.process.join()

    def run(self) -> None:
        try:
            while not self.found.is_set():
                params = self.queue.get(timeout=10)
                if ans := self.crack(params):
                    self.found.set()
                    print(ans)
                    return
        except Empty:
            return

    @abstractmethod
    def crack(self, params: HashParameter):
        ...


def run_crack(
    cracker: CrackManager, queue: multiprocessing.Queue, found: multiprocessing.Event
) -> list[multiprocessing.Process]:
    return [cracker(queue, found).start() for _ in range(multiprocessing.cpu_count())]