"""
Regression test: dev-tools must NOT have a 'profiles' key in docker-compose.prod.yml.

Root cause (April 2026): dev-tools had `profiles: [dev-tools]` in prod compose.
Any `docker-compose up -d` (e.g. after backend rebuild) skipped dev-tools silently,
causing 502 errors on /cpanel/api/capture requests.
"""
import yaml
import pathlib


COMPOSE_PROD = pathlib.Path(__file__).parents[2] / "docker-compose.prod.yml"


def _load_compose():
    with COMPOSE_PROD.open() as f:
        return yaml.safe_load(f)


def test_dev_tools_has_no_profile_in_prod():
    """dev-tools must not be behind a 'profiles' key in docker-compose.prod.yml.

    If profiles are set, `docker-compose up -d` skips the container silently,
    causing 502 errors on every /cpanel API call.
    """
    compose = _load_compose()
    service = compose.get("services", {}).get("dev-tools")
    assert service is not None, "dev-tools service is missing from docker-compose.prod.yml"
    assert "profiles" not in service, (
        "dev-tools has 'profiles' in docker-compose.prod.yml — "
        "this means it won't start with regular `docker-compose up -d`, "
        "causing 502 on /cpanel endpoints."
    )


def test_dev_tools_on_drscribe_network():
    """dev-tools must be on drscribe-network so parent-website can reach it."""
    compose = _load_compose()
    service = compose.get("services", {}).get("dev-tools", {})
    networks = list((service.get("networks") or {}).keys()) if isinstance(
        service.get("networks"), dict
    ) else (service.get("networks") or [])
    assert "drscribe-network" in networks, (
        "dev-tools is not on drscribe-network — "
        "parent-website (cpanel) cannot reach it, causing 502."
    )


def test_dev_tools_has_restart_policy():
    """dev-tools must have a restart policy so it recovers after server reboots."""
    compose = _load_compose()
    service = compose.get("services", {}).get("dev-tools", {})
    restart = service.get("restart")
    assert restart in ("always", "unless-stopped", "on-failure"), (
        f"dev-tools restart policy is '{restart}' — "
        "it won't restart automatically after a server reboot or crash."
    )
