

from scenario import Scenario
from utils import cmd
import asyncio

API = '36d9e750-f50c-442d-ba32-1cec72a04d4c'


class KomodorAgentScenario(Scenario):

    def __init__(self, kubeconfig):
        super().__init__("komodor-agent", kubeconfig)

    async def run(self):
        await asyncio.sleep(60) # Wait x seconds before deploying, to let other deployments to finish

        self.log("Starting to deploy")
        install_cmd = (f"{self.helm} upgrade --install komodor-agent komodorio/komodor-agent "
                       f"--set apiKey={API} "
                       f"--set clusterName=agent-release-checks")
        output, exit_code = await cmd(install_cmd, silent=True)
        if exit_code != 0:
            self.error(f"Failed to deploy: {output}")
            raise Exception(f"Failed to deploy: {self.name}")
        self.log("Finished deploying")

    async def cleanup(self):
        self.log(f"Uninstalling {self.name}")
        await cmd(f"{self.helm} uninstall komodor-agent")
