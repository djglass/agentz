import subprocess
import json

def get_latest_local_api_url():
    """Returns the latest LocalStack API Gateway URL."""
    try:
        result = subprocess.run(
            ["awslocal", "apigateway", "get-rest-apis"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        if result.returncode != 0:
            raise RuntimeError(f"awslocal error: {result.stderr.strip()}")

        apis = json.loads(result.stdout).get("items", [])
        if not apis:
            raise RuntimeError("No APIs found in LocalStack.")

        # Pick the most recently created API
        latest_api = sorted(apis, key=lambda x: x["createdDate"], reverse=True)[0]
        api_id = latest_api["id"]

        return f"http://localhost:4566/restapis/{api_id}/v1/_user_request_/hello"

    except Exception as e:
        return f"❌ Error retrieving local API URL: {e}"
