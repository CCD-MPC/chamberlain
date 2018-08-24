import os

from time import sleep

from src.conclave_manager import JiffServer
from src.conclave_manager.compute_party import ComputeParty


class ConclaveManager:
    """
    Generates and launches JiffServer & ComputeParty objects
    """

    def __init__(self, json_data, app, compute_id):

        self.app = app
        self.protocol_config = json_data

        self.template_directory = "{}/templates/".format(os.path.dirname(os.path.realpath(__file__)))
        self.timestamp = compute_id
        self.jiff_server = JiffServer(app, self.timestamp)
        self.protocol = self.load_protocol()
        self.compute_parties = self.create_compute_parties()

    def query_jiff_server(self):
        """
        Query IP address of JiffServer.
        Halts creation of ComputeParty objects until resolved.
        """

        ready = False
        ip = None

        while not ready:

            ip = self.jiff_server.query_server_ip()

            if ip is not None:
                ready = True
            else:
                sleep(5)

        return ip

    def load_protocol(self):
        """
        Load protocol from protocol_config and log result.
        """

        protocol = self.protocol_config['protocol']
        self.app.logger.info("CC Protocol:\n{}".format(protocol))

        return protocol

    def create_compute_parties(self):
        """
        Init all compute parties.
        """

        server_ip = self.query_jiff_server()

        self.app.logger.info("Server IP for Job {0}: {1}".format(self.timestamp, server_ip))

        all_pids = list(range(1, len(self.protocol_config['config']['dataRows']) + 1))
        compute_parties = []

        self.app.logger.info(
            "Creating Conclave Pod templates for {} parties"
                .format(str(len(all_pids))))

        '''
        TODO: will need to resolve ownership between datasets, and 
        create a compute party for each unique data owner (i.e. - 
        case when a single party owns more than one dataset). No 
        point in doing this until we incorporate the DataVerse API, though.
        '''

        for i in all_pids:
            compute_parties.append(
                ComputeParty(
                    i,
                    all_pids,
                    self.timestamp,
                    self.protocol,
                    self.app,
                    self.protocol_config['config']['dataRows'][i-1],
                    server_ip)
            )

        return compute_parties

    def run(self):
        """
        Wraps main class methods.
        """

        self.app.logger.info(
            "Launching Conclave pods for the following compute parties:\n{}"
                .format("\n".join(job.name for job in self.compute_parties)))

        for party in self.compute_parties:
            party.launch()





