import os

from time import sleep

from src.conclave_manager.jiff_server import JiffServer
from src.conclave_manager.compute_party import ComputeParty


class ConclaveManager:
    """
    Generates and launches JiffServer & ComputeParty objects
    """

    def __init__(self, json_data, app, db_model):

        self.app = app
        self.protocol_config = json_data
        self.db_model = db_model

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
        """

        protocol = self.protocol_config['protocol']["data"]
        self.app.logger.info("CC Protocol:\n{}".format(protocol))

        return protocol

    def resolve_namespaces(self):

        ret = []

        datasets = self.protocol_config['data']['endpoints']

        for d in datasets:

            dset_id = "{0}_{1}".format(d["containerName"], d["fileName"])
            lookup = self.db_model.query.filter_by(dataset_id=dset_id).first()

            if lookup is not None:
                ret.append(lookup.namespace)
            else:
                ret.append("cici")

        self.app.logger.info("Namespace map for workflow {0}: {1}".format(self.compute_id, ret))

        return ret

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
        namespace_lookups = self.resolve_namespaces()

        compute_parties = []

        self.app.logger.info("Creating Conclave Pod templates for {} parties"
                             .format(str(len(all_pids))))

        for i in all_pids:
            compute_parties.append(
                ComputeParty(
                    i,
                    all_pids,
                    self.compute_id,
                    self.protocol,
                    self.app,
                    self.protocol_config,
                    namespace_lookups,
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
