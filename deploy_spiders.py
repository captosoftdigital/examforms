import os
import sys
import subprocess
from scrapyd_client import deploy

def main():
    print("Deploying spiders to ScrapyD...")
    
    # Check if ScrapyD is running
    try:
        # This is a simple check, strictly speaking deploy() handles interaction
        # But we can try to ping it
        import requests
        resp = requests.get('http://localhost:6800/daemonstatus.json')
        if resp.status_code != 200:
            print("ScrapyD is not returning 200 OK. Is it running?")
            return
    except Exception as e:
        print(f"Count not connect to ScrapyD at localhost:6800. Please ensure it is running.\nError: {e}")
        # We can still try to deploy if the user knows what they are doing, or just exit.
        # But scrapyd-deploy might handle it.
        
    # Use scrapyd-deploy from command line for simplicity as it handles egg building
    # or use Python API if available.
    # The standard way is `scrapyd-deploy <target>`
    
    # We'll use subprocess to call scrapyd-deploy
    try:
        # Assumes scrapy.cfg is in current directory
        subprocess.check_call(["scrapyd-deploy", "default"])
        print("Deployment successful!")
    except subprocess.CalledProcessError as e:
        print(f"Deployment failed: {e}")
    except FileNotFoundError:
        print("scrapyd-deploy not found. Please install scrapyd-client.")

if __name__ == "__main__":
    main()
