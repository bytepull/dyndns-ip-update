import os
import sys
import ipaddress
import socket
import requests
from datetime import datetime, timezone

DOMAIN = os.environ.get("DYNDNS_DOMAIN")
USERNAME = os.environ.get("DYNDNS_USERNAME")
PASSWORD = os.environ.get("DYNDNS_PASSWORD")

IPIFY_URL = "https://api.ipify.org?format=json"
DYNDNS_URL = "https://update.dyndns.it/"


def get_public_ip():
    response = requests.get(IPIFY_URL, timeout=15)
    response.raise_for_status()

    ip_address = response.json()["ip"]
    return str(ipaddress.ip_address(ip_address))


def get_dns_ip(domain):
    try:
        return socket.gethostbyname(domain)
    except socket.gaierror:
        return None


def update_dyndns():
    if not all([DOMAIN, USERNAME, PASSWORD]):
        print("ERROR: Missing DynDNS configuration", flush=True)
        sys.exit(1)

    try:
        timestamp = datetime.now(timezone.utc).isoformat()

        print(f"[{timestamp}] Checking public IP...", flush=True)

        # Get current public IP
        public_ip = get_public_ip()
        print(f"Public IP: {public_ip}", flush=True)

        # Get IP currently associated with the domain
        dns_ip = get_dns_ip(DOMAIN)
        print(f"DynDNS IP: {dns_ip}", flush=True)

        # Compare IP addresses
        if public_ip == dns_ip:
            print("IP unchanged. No update required.", flush=True)
            return

        print("IP changed! Updating DynDNS...", flush=True)

        params = {
            "hostname": DOMAIN,
            "myip": public_ip
        }

        response = requests.get(
            DYNDNS_URL,
            params=params,
            auth=(USERNAME, PASSWORD),
            timeout=15
        )

        response.raise_for_status()

        print(
            f"DynDNS response: {response.text.strip()}",
            flush=True
        )

        print("DynDNS update completed.", flush=True)

    except requests.exceptions.RequestException as e:
        print(f"Network error: {e}", flush=True)
        sys.exit(1)

    except (KeyError, ValueError) as e:
        print(f"Invalid IP response: {e}", flush=True)
        sys.exit(1)


if __name__ == "__main__":
    update_dyndns()