from subprocess import run

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
        run(["bandit", "--recursive", "--format", "txt", "plateypus"])
        run(["pylint", "--jobs=0", "plateypus"])
