import os

from time import sleep

from conclave_manager.jiff_server import JiffServer
from conclave_manager.compute_party import ComputeParty


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

    def query_pod_status(self):
        """
        Need some kind of protocol for querying status of all pods and deleting
        all object associated with them once they have status "Completed". API
        for necessary function is here:
        https://github.com/kubernetes-client/python/blob/master/kubernetes/docs/CoreV1Api.md#read_namespaced_pod_status
        """

        return

    def load_protocol(self):
        """
        TODO: Will later load this from self.protocol_config.protocol
        """

        mock_data_directory = "{}/mock_data".format(os.path.dirname(os.path.realpath(__file__)))
        protocol = open("{}/protocol.py".format(mock_data_directory)).read()

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
        for each submitted dataset, create a ComputeParty
        
        TODO: will need to resolve ownership between datasets, and 
        create a compute party for each unique data owner (i.e. - 
        case when a single party owns more than one dataset).
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





