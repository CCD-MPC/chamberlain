import os

from time import sleep

from src.conclave_manager.jiff_server import JiffServer
from src.conclave_manager.compute_party import ComputeParty


class ConclaveManager:
    """
    Generates and launches JiffServer & ComputeParty objects
    """

    def __init__(self, json_data, app):

        self.app = app
        self.protocol_config = json_data

        self.template_directory = "{}/templates/".format(os.path.dirname(os.path.realpath(__file__)))
        self.compute_id = json_data["config"]["ID"]
        self.jiff_server = self.build_jiff_server()
        self.protocol = self.load_protocol()
        self.compute_parties = self.create_compute_parties()

    def build_jiff_server(self):

        if len(self.protocol_config["data"]["endpoints"]) == 2:
            return "N/A"
        elif len(self.protocol_config["data"]["endpoints"]) > 2:
            return JiffServer(self.app, self.compute_id, self.protocol_config)
        else:
            self.app.logger.error("You must pass at least two endpoints. \n")

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

        # TODO implement b64 encoded form for protocol
        """

        protocol = self.protocol_config['protocol']["data"]
        self.app.logger.info("CC Protocol:\n{}".format(protocol))

        return protocol

    def create_compute_parties(self):
        """
        Init all compute parties.
        """

        if self.jiff_server != "N/A":
            server_ip = self.query_jiff_server()
            self.app.logger.info("Server IP for Job {0}: {1}".format(self.compute_id, server_ip))
        else:
            server_ip = "N/A"

        all_pids = list(range(1, len(self.protocol_config['data']['endpoints']) + 1))

        compute_parties = []

        self.app.logger.info("Creating Conclave Pod templates for {} parties"
                             .format(str(len(all_pids))))

        '''
        TODO: will need to resolve ownership between datasets, and 
        create a compute party for each unique data owner (i.e. - 
        case when a single party stores more than one dataset).
        
        Might be able to resolve via aliases in the metadata for
        DV endpoints.
        
        For Swift, we'll need a DB that maps authURL's to openshift clusters/namespaces
        '''

        for i in all_pids:
            compute_parties.append(
                ComputeParty(
                    i,
                    all_pids,
                    self.compute_id,
                    self.protocol,
                    self.app,
                    self.protocol_config,
                    server_ip)
                )

        return compute_parties

    def run(self):
        """
        Launch all ComputeParty objects, if they exist.
        """

        if self.compute_parties is None:
            self.app.logger.error(
                "No compute parties, nothing to run. \n "
                "This likely means that no endpoints for input "
                "data were passed to the ConclaveManager.")
            return

        self.app.logger.info(
            "Launching Conclave pods for the following compute parties:\n{}"
                .format("\n".join(job.name for job in self.compute_parties)))

        for party in self.compute_parties:
            party.launch()
