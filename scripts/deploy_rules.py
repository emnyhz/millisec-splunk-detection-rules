import os
import sys
import glob
import urllib.parse

import yaml
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

SPLUNK_URL = os.getenv("SPLUNK_URL", "https://127.0.0.1:8089")
SPLUNK_TOKEN = os.getenv("SPLUNK_TOKEN")

if not SPLUNK_TOKEN:
    print("ERROR: SPLUNK_TOKEN is not configured.")
    sys.exit(1)

HEADERS = {
    "Authorization": f"Bearer {SPLUNK_TOKEN}"
}


def load_rules():
    rule_files = sorted(
        glob.glob("rules/**/*.yml", recursive=True)
    )

    if not rule_files:
        print("ERROR: No rule files found.")
        sys.exit(1)

    return rule_files


def deploy_rule(rule_file):
    with open(rule_file, "r", encoding="utf-8") as f:
        rule = yaml.safe_load(f)

    rule_id = rule["id"]
    splunk = rule["splunk"]
    search_name = splunk["name"]

    payload = {
        "search": rule["search"],
        "description": (
            f"[{rule_id}] {rule['description'].strip()} "
            f"| Severity: {rule['severity']} "
            f"| Managed by GitHub"
        ),
        "is_scheduled": "1",
        "cron_schedule": splunk["schedule"],
        "dispatch.earliest_time": splunk["earliest_time"],
        "dispatch.latest_time": splunk["latest_time"],
        "alert_type": splunk["alert_type"],
        "alert_comparator": splunk["alert_comparator"],
        "alert_threshold": str(splunk["alert_threshold"]),
        "alert.track": "1",
        "alert.suppress": "1",
        "alert.suppress.period": str(
            splunk.get("throttle_seconds", 60)
        ),
        "disabled": "0",
        "is_visible": "1",
        "output_mode": "json"
    }

    encoded_name = urllib.parse.quote(search_name, safe="")

    check_url = (
        f"{SPLUNK_URL}/servicesNS/nobody/search/"
        f"saved/searches/{encoded_name}"
    )

    check = requests.get(
        check_url,
        headers=HEADERS,
        params={"output_mode": "json"},
        verify=False,
        timeout=30
    )

    if check.status_code == 200:
        action = "UPDATE"
        response = requests.post(
            check_url,
            headers=HEADERS,
            data=payload,
            verify=False,
            timeout=30
        )
    elif check.status_code == 404:
        action = "CREATE"

        create_url = (
            f"{SPLUNK_URL}/servicesNS/nobody/search/"
            f"saved/searches"
        )

        create_payload = {
            "name": search_name,
            **payload
        }

        response = requests.post(
            create_url,
            headers=HEADERS,
            data=create_payload,
            verify=False,
            timeout=30
        )
    else:
        print(
            f"[ERROR] {rule_id}: unable to check existing rule "
            f"(HTTP {check.status_code})"
        )
        print(check.text)
        return False

    if response.status_code in (200, 201):
        print(
            f"[{action}] {rule_id} -> {search_name} "
            f"[HTTP {response.status_code}]"
        )
        return True

    print(
        f"[ERROR] {rule_id} deployment failed "
        f"[HTTP {response.status_code}]"
    )
    print(response.text)
    return False


def main():
    files = load_rules()

    print(f"Found {len(files)} detection rules.")
    print("-" * 60)

    failures = 0

    for rule_file in files:
        try:
            if not deploy_rule(rule_file):
                failures += 1
        except Exception as exc:
            failures += 1
            print(f"[ERROR] {rule_file}: {exc}")

    print("-" * 60)

    if failures:
        print(f"Deployment completed with {failures} failure(s).")
        sys.exit(1)

    print(f"Successfully synchronized {len(files)} rules with Splunk.")


if __name__ == "__main__":
    main()
