import time
from config import BE_BASE_URL
from fixtures import setup_cluster, cleanup_agent_from_cluster
from helpers.utils import cmd, get_filename_as_cluster_name
from helpers.helm_helper import helm_agent_install
from helpers.komodor_helper import create_komodor_uid, query_backend

CLUSTER_NAME = get_filename_as_cluster_name(__file__)


# define events.watchnamespace
def test_define_events_watchnamespace(setup_cluster):
    def query_events(namespace, deployment, start_time, end_time):
        kuid = create_komodor_uid("Deployment", deployment, namespace, CLUSTER_NAME)
        url = f"{BE_BASE_URL}/resources/api/v1/events/general?fromEpoch={start_time}&toEpoch={end_time}&komodorUids={kuid}"
        return query_backend(url)

    watch_namespace = "client-namespace"
    watch_deployment = "nc-client"
    un_watch_namespace = "server-namespace"
    un_watch_deployment = "nc-server"
    start_time = int(time.time() * 1000)

    output, exit_code = helm_agent_install(CLUSTER_NAME, additional_settings=f"--set capabilities.events.watchNamespace={watch_namespace}")
    assert exit_code == 0, f"Agent installation failed, output: {output}"

    # Create deploy event
    cmd(f'kubectl rollout restart deployment/{watch_deployment} -n {watch_namespace}')
    cmd(f'kubectl rollout restart deployment/{un_watch_deployment} -n {un_watch_namespace}')

    # Wait for event to be sent
    time.sleep(10)
    end_time = int(time.time() * 1000) + 120_000  # two minutes from now

    # Verify events from watched namespace
    response = query_events(watch_namespace, watch_deployment, start_time, end_time)
    assert response.status_code == 200, f"Failed to get configmap from resources api, response: {response}"
    assert len(response.json()['event_deploy']) > 0, f"Failed to get event_deploy from resources api, response: {response}"

    # Verify that we dont get events from unwatched namespace
    response = query_events(un_watch_namespace, un_watch_deployment, start_time, end_time)
    assert response.status_code == 200, f"Failed to get configmap from resources api, response: {response}"
    assert len(response.json()['event_deploy']) == 0, f"Failed to get event_deploy from resources api, response: {response}"


# Block namespace and validate that no events are sent
def test_block_namespace(setup_cluster):
    def query_events(namespace, deployment, start_time, end_time):
        kuid = create_komodor_uid("Deployment", deployment, namespace, CLUSTER_NAME)
        url = f"{BE_BASE_URL}/resources/api/v1/events/general?fromEpoch={start_time}&toEpoch={end_time}&komodorUids={kuid}"
        return query_backend(url)

    un_watch_namespace = "client-namespace"
    un_watch_deployment = "nc-client"
    watch_namespace = "server-namespace"
    watch_deployment = "nc-server"
    start_time = int(time.time() * 1000)

    output, exit_code = helm_agent_install(CLUSTER_NAME, additional_settings=f"--set capabilities.events.namespacesDenylist={{{un_watch_namespace}}}")
    assert exit_code == 0, f"Agent installation failed, output: {output}"

    # Create deploy event
    cmd(f'kubectl rollout restart deployment/{watch_deployment} -n {watch_namespace}')
    cmd(f'kubectl rollout restart deployment/{un_watch_deployment} -n {un_watch_namespace}')

    # Wait for event to be sent
    time.sleep(10)
    end_time = int(time.time() * 1000) + 120_000  # two minutes from now

    # Verify events from watched namespace
    response = query_events(watch_namespace, watch_deployment, start_time, end_time)
    assert response.status_code == 200, f"Failed to get configmap from resources api, response: {response}"
    assert len(response.json()['event_deploy']) > 0, f"Failed to get event_deploy from resources api, response: {response}"

    # Verify that we dont get events from unwatched namespace
    response = query_events(un_watch_namespace, un_watch_deployment, start_time, end_time)
    assert response.status_code == 200, f"Failed to get configmap from resources api, response: {response}"
    assert len(response.json()['event_deploy']) == 0, f"Failed to get event_deploy from resources api, response: {response}"