from prefect.deployments import Deployment
from parameterized_flow import etl_parent_flow
from prefect.filesystems import GitHub

github_dep = Deployment.build_from_flow(
    flow=etl_parent_flow,
    name="github-flow-q4",
    parameters={"year":2020, "color":"green", "months":[11]},
    storage=GitHub.load("prefect-github"),
    entrypoint="parameterized_flow.py:etl_parent_flow"
)

if __name__ == "__main__":
    github_dep.apply()