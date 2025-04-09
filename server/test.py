import subprocess
import sys


def run():
    try:
        subprocess.run(["coverage", "run", "-m", "pytest"], check=True)
        # Only assess coverage if all tests pass
        subprocess.run(["coverage", "report"], check=True)
        subprocess.run(["coverage", "html"], check=True)
    except subprocess.CalledProcessError:
        sys.exit(1)


if __name__ == "__main__":
    run()
