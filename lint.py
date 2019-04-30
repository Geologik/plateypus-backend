"""Run a chain of analysis tools and linters: isort → black → pylint → bandit."""

from subprocess import run

if __name__ == "__main__":
    isort = run(
        [
            "isort",
            "--apply",
            "--atomic",
            "--recursive",
            "--combine-as",
            "--combine-star",
            "--multi-line=3",
            "--trailing-comma",
            "--force-grid-wrap=0",
            "--use-parentheses",
            "--line-width=88",
        ]
    )

    if isort.returncode == 0:
        black = run(["black", "."])

        if black.returncode == 0:
            run(["pylint", "plateypus"])
            run(["bandit", "--recursive", "--format", "txt", "plateypus"])
