"""Start clean dockerized Elasticsearch and Kibana servers,
as well as an APM Server if the APM_PATH environment variable is set.
"""

from os import environ
from subprocess import run

if __name__ == "__main__":
    APM_PATH = environ.get("APM_PATH")
    DOCKER = "docker"
    NAME_ELASTICSEARCH = "plateypus_elastic"
    NAME_KIBANA = "plateypus_kibana"

    for container in (NAME_ELASTICSEARCH, NAME_KIBANA):
        stop = run([DOCKER, "stop", container])
        if stop.returncode == 0:
            rm = run([DOCKER, "rm", container])

    run(
        [
            DOCKER,
            "run",
            "--detach",
            "--name",
            NAME_ELASTICSEARCH,
            "--publish",
            "9200:9200",
            "--publish",
            "9300:9300",
            "--env",
            '"discovery.type=single-node"',
            "docker.elastic.co/elasticsearch/elasticsearch:7.0.0",
        ]
    )
    run(
        [
            DOCKER,
            "run",
            "--detach",
            "--name",
            NAME_KIBANA,
            "--publish",
            "5601:5601",
            "docker.elastic.co/kibana/kibana:7.0.0",
        ]
    )

    if APM_PATH is not None:
        run([f"{APM_PATH}/apm-server", "-e"])
