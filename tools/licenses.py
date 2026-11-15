"""Tell open source licenses apart, using the SPDX license list's OSI flag."""

import http.client
import json
import urllib.request

SPDX_LICENSES = "https://spdx.org/licenses/licenses.json"
TIMEOUT_SECONDS = 30


class LicenseListError(Exception):
    pass


def osi_approved() -> frozenset[str]:
    """Return the SPDX identifiers of the licenses the OSI approved."""
    request = urllib.request.Request(
        SPDX_LICENSES, headers={"User-Agent": "awesome-discogs-checks"}
    )
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
            licenses = json.load(response)["licenses"]
    except (OSError, http.client.HTTPException, ValueError, KeyError) as error:
        raise LicenseListError(f"GET {SPDX_LICENSES} failed: {error}") from error
    return frozenset(
        license["licenseId"] for license in licenses if license.get("isOsiApproved")
    )
