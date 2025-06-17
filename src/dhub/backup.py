import subprocess
from datetime import datetime


def backup():
    now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    print(f"Syncing data: {now}")

    try:
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", now], check=True)
        subprocess.run(["git", "push"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Git command failed: {e}")
