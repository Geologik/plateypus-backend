"""Start a clean dockerized Elasticsearch server"""

from subprocess import run

if __name__ == "__main__":
    DOCKER = "docker"
    CONTAINER_NAME = "plateypus_elastic"

    stop = run([DOCKER, "stop", CONTAINER_NAME])
    if stop.returncode == 0:
        rm = run([DOCKER, "rm", CONTAINER_NAME])

    run(
        [
            DOCKER,
            "run",
            "--detach",
            "--name",
            CONTAINER_NAME,
            "--publish",
            "9200:9200",
            "--publish",
            "9300:9300",
            "--env",
            '"discovery.type=single-node"',
            "docker.elastic.co/elasticsearch/elasticsearch:7.0.1",
        ]
    )
