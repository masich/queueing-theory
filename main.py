from event_listener import ListenerManager
from model import ImitationModel
from models.client import ClientGenerator, ClientStorage
from models.manager import ServerManager
from models.server import Server
from settings import SIMULATION_TIME, SERVERS_COUNT, PROCESSING_DISTRIBUTION, ARRIVAL_DISTRIBUTION
from statistic.statistician import Statistician

if __name__ == '__main__':
    client_generator = ClientGenerator()
    listener_manager = ListenerManager()
    queue = ClientStorage()
    servers = [Server(PROCESSING_DISTRIBUTION, listener_manager) for _ in range(SERVERS_COUNT)]
    manager = ServerManager(servers, queue, listener_manager)
    statistician = Statistician(queue, servers)
    listener_manager.add_listener(statistician)

    ImitationModel(ARRIVAL_DISTRIBUTION, client_generator, SIMULATION_TIME, servers, manager, listener_manager).run()

    statistician.print_statistics()
