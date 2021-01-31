from typing import Iterable, Tuple


from common import Printable
from models.client import ClientStorage, Client, ClientListener
from models.server import Server
from statistic.metrics import AverageMetric, TimeMetric, SystemMetric
from utils import Stopwatch


class Statistician(ClientListener, Printable):
    def __init__(self, storage: ClientStorage, servers: Iterable[Server]):
        self._storage, self._servers = storage, servers
        self._processing_metrics, self._waiting_metrics = [], []
        self._load_metric = AverageMetric()
        self._queue_size_metric = AverageMetric()
        self._busyness_metric = SystemMetric()

        self._processing_times, self._queue_times = {}, {}

    def on_arrived(self, client: Client) -> None:
        pass

    def on_scheduled(self, client: Client):
        self._print(f'{client} has been scheduled.')
        self._record_queue_size()
        self._record_load()
        self._busyness_metric.record_busy()

    def on_processing_started(self, client: Client) -> None:
        self._processing_times[client.id] = Stopwatch()
        self._print(f'processing of the {client} has been started.')

    def on_processing_finished(self, client: Client) -> None:
        self._record_queue_size()
        self._record_load()
        self._record_client_finish(client)

        if self._is_system_idle():
            self._busyness_metric.record_idle()

    def on_all_processed(self):
        self._busyness_metric.stop_record()

    def on_queued(self, client: Client) -> None:
        self._print(f'{client} has been queued.')
        self._queue_times[client.id] = Stopwatch()

    def on_popped_from_queue(self, client: Client) -> None:
        self._print(f'{client} has been popped from queue.')
        stopwatch = self._queue_times.pop(client.id)
        self._waiting_metrics.append(TimeMetric(client, stopwatch.milliseconds_since_start))

    def print_statistics(self):
        _, avg_process_time, _ = self._process_time()
        _, avg_queue_time, _ = self._queue_time()
        avg_queue_size = self._queue_size_metric.average
        avg_load = self._load_metric.average
        idle_probability = self._idle_probability()
        self._print('general statistics are provided below.')
        self._print('average clients in the system:  ', avg_load, 'clients.', sep=' ')
        self._print('average client processing time: ', avg_process_time, 'milliseconds.', sep=' ')
        self._print('average queue size:             ', avg_queue_size, 'clients.', sep=' ')
        self._print('average time in the queue:      ', avg_queue_time, 'milliseconds.', sep=' ')
        self._print('chance of system downtime:      ', idle_probability, '%.', sep=' ')

    def _record_client_finish(self, client: Client) -> None:
        stopwatch = self._processing_times.pop(client.id)
        since_start = stopwatch.milliseconds_since_start
        self._processing_metrics.append(TimeMetric(client, since_start))
        self._print(f'{client} has been processed for {since_start} milliseconds.')

    def _record_load(self) -> None:
        clients_count = 0
        for server in self._servers:
            clients_count += server.client is not None

        self._load_metric.add(clients_count + len(self._storage))

    def _record_queue_size(self) -> None:
        self._queue_size_metric.add(len(self._storage))

    def _process_time(self) -> Tuple[int, int, float]:
        time_per_client = [stat.time for stat in self._processing_metrics]
        total_time = sum(time_per_client)
        clients_count = len(time_per_client)
        avg_time = (total_time / clients_count) if clients_count else 0
        return total_time, avg_time, clients_count

    def _queue_time(self) -> Tuple[int, int, float]:
        time_per_client = [stat.time for stat in self._waiting_metrics]
        total_time = sum(time_per_client)
        queued_clients_count = len(time_per_client)
        avg_time = (total_time / queued_clients_count) if queued_clients_count else 0
        return total_time, avg_time, queued_clients_count

    def _idle_probability(self) -> float:
        idle_time = self._busyness_metric.idle_time()

        total_time = self._busyness_metric.busy_time() + idle_time
        self._print(f'total time is {total_time} milliseconds.')

        return round((idle_time / total_time) * 100, 3)

    def _is_system_idle(self) -> bool:
        return not self._storage and all(self._servers)
