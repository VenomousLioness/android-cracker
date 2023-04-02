import multiprocessing
from io import BufferedReader
from multiprocessing.queues import Queue

from cracker.AbstractCracker import AbstractCracker
from cracker.CrackManager import CrackManager, HashParameter, run_crack
from cracker.exception import MissingArgumentException
from cracker.policy import DevicePolicy


class AbstractPINCracker(AbstractCracker):
    def __init__(
        self,
        file: BufferedReader,
        device_policy: DevicePolicy | None,
        cracker: type[CrackManager],
    ):
        if device_policy is None:
            raise MissingArgumentException("Length or policy argument is required")
        super().__init__(file, cracker)
        self.device_policy = device_policy

    def run(self) -> None:
        queue: Queue[HashParameter] = multiprocessing.Queue()
        found = multiprocessing.Event()
        result: Queue[str] = multiprocessing.Queue()
        crackers = run_crack(self.cracker, queue, found, result)

        for possible_pin in range(10**self.device_policy.length):
            if found.is_set():
                for cracker in crackers:
                    cracker.stop()
                break
            queue.put(self.generate_hashparameters(possible_pin))

        for cracker in crackers:
            cracker.join()
        queue.cancel_join_thread()
        print(f"Found key: {result.get()}")
