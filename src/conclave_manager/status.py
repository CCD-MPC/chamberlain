from kubernetes import client as k_client
from kubernetes import config as k_config
from kubernetes.client.rest import ApiException


def construct_object_strings(job_id, num_parties):
    """
    Given <job_id> and <num_parties>, return names of all pods involved in that computation.
    """

    jiff_server_str = ["jiff-server-{}".format(job_id)]
    compute_party_pods = []

    for i in range(1, num_parties + 1):
        compute_party_pods.append("conclave-{0}-{1}".format(job_id, i))

    return jiff_server_str + compute_party_pods


def check_pod_status(job_id, num_parties, app):
    """
    Query pod status for all pods with the given <job_id>.
    """

    k_config.load_incluster_config()
    kube_client = k_client.CoreV1Api()

    pods = construct_object_strings(job_id, num_parties)

    app.logger.info("Checking status for the following Pods: {}"
                    .format("\n".join(cc for cc in pods)))

    statuses = []

    for p in pods:
        try:
            status = kube_client.read_namespaced_pod_status(p, "cici", pretty="true")
            app.logger.info("Status for {0}: {1}".format(p, status))
            statuses.append(status)
        except ApiException as e:
            app.logger.error("Error checking status for Pod {0}: {1}".format(p, e))
            statuses.append(e)

    return statuses
