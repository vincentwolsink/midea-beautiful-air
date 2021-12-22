""" Discover Midea Humidifiers on local network using command-line """
from __future__ import annotations

try:
    from coloredlogs import install as coloredlogs_install
except Exception:

    def coloredlogs_install(level):
        pass


from argparse import ArgumentParser
import logging

from midea_beautiful_dehumidifier import (
    appliance_state,
    connect_to_cloud,
    find_appliances,
)
from midea_beautiful_dehumidifier.lan import LanDevice
from midea_beautiful_dehumidifier.midea import DEFAULT_APP_ID, DEFAULT_APPKEY

_LOGGER = logging.getLogger(__name__)


def output(appliance: LanDevice, show_credentials: bool = False):
    print(f"addr={appliance.ip}:{appliance.port}")
    print(f"        id      = {appliance.id}")
    print(f"        s/n     = {appliance.sn}")
    print(f"        model   = {appliance.model}")
    print(f"        ssid    = {appliance.ssid}")
    print(f"        online  = {appliance.online}")
    print(f"        name    = {getattr(appliance.state, 'name')}")
    print(f"        humid%  = {getattr(appliance.state, 'current_humidity')}")
    print(f"        target% = {getattr(appliance.state, 'target_humidity')}")
    print(f"        fan     = {getattr(appliance.state, 'fan_speed')}")
    print(f"        tank    = {getattr(appliance.state, 'tank_full')}")
    print(f"        mode    = {getattr(appliance.state, 'mode')}")
    print(f"        ion     = {getattr(appliance.state, 'ion_mode')}")
    if show_credentials:
        print(f"        token   = {appliance.token}")
        print(f"        key     = {appliance.key}")


def cli() -> None:
    parser = ArgumentParser(
        prog="midea_beautiful_dehumidifier.cli",
        description="Discovers and manages Midea dehumidifiers on local network(s).",
    )

    parser.add_argument(
        "--log",
        help="sets logging level (numeric or one of python logging levels) ",
        default="WARNING",
    )
    subparsers = parser.add_subparsers(help="sub-commands", dest="command")

    parser_discover = subparsers.add_parser(
        "discover",
        help="discovers appliances on local network(s)",
        description="Discovers appliances on local network(s)",
    )
    parser_discover.add_argument("--account", help="Midea app account", required=True)
    parser_discover.add_argument("--password", help="Midea app password", required=True)
    parser_discover.add_argument(
        "--appkey",
        help="Midea app key",
        default=DEFAULT_APPKEY,
    )
    parser_discover.add_argument(
        "--appid",
        help="Midea app id. Note that appid must correspond to app key",
        default=DEFAULT_APP_ID,
    )
    parser_discover.add_argument(
        "--credentials", action="store_true", help="show credentials in output"
    )
    parser_discover.add_argument(
        "--network",
        nargs="+",
        help="network range(s) for discovery (e.g. 192.0.0.0/24).",
    )

    parser_status = subparsers.add_parser(
        "status",
        help="gets status from appliance",
        description="Gets status from appliance.",
    )
    parser_status.add_argument(
        "--ip", help="IP address of the appliance", required=True
    )
    parser_status.add_argument(
        "--token",
        help="token used to communicate with appliance",
        default="",
    )
    parser_status.add_argument(
        "--key", help="key used to communicate with appliance", default=""
    )
    parser_status.add_argument("--account", help="Midea app account", required=True)
    parser_status.add_argument("--password", help="Midea app password", required=True)
    parser_status.add_argument(
        "--appkey",
        help="Midea app key",
        default=DEFAULT_APPKEY,
    )
    parser_status.add_argument(
        "--appid",
        help="Midea app id. Note that appid must correspond to app key",
        default=DEFAULT_APP_ID,
    )
    parser_status.add_argument(
        "--credentials", action="store_true", help="show credentials in output"
    )

    parser_set = subparsers.add_parser(
        "set",
        help="sets status of appliance",
        description="Sets status of an appliance.",
    )
    parser_set.add_argument("--ip", help="IP address of the appliance", required=True)
    parser_set.add_argument(
        "--token",
        help="token used to communicate with appliance",
        default="",
    )
    parser_set.add_argument(
        "--key", help="key used to communicate with appliance", default=""
    )
    parser_set.add_argument("--account", help="Midea app account", required=True)
    parser_set.add_argument("--password", help="Midea app password", required=True)
    parser_set.add_argument(
        "--appkey",
        help="Midea app key",
        default=DEFAULT_APPKEY,
    )
    parser_set.add_argument(
        "--appid",
        help="Midea app id. Note that appid must correspond to app key",
        default=DEFAULT_APP_ID,
    )
    parser_set.add_argument(
        "--credentials", action="store_true", help="show credentials in output"
    )
    parser_set.add_argument("--humidity", help="target humidity", default=None)
    parser_set.add_argument("--fan", help="fan strength", default=None)
    parser_set.add_argument("--mode", help="dehumidifier mode switch", default=None)
    parser_set.add_argument("--ion", help="ion mode switch", default=None)
    parser_set.add_argument("--on", help="turn on/off", default=None)

    args = parser.parse_args()
    log_level = int(args.log) if args.log.isdigit() else args.log
    try:
        coloredlogs_install(level=log_level)
    except Exception:
        logging.basicConfig(level=log_level)

    if args.command == "discover":
        appliances = find_appliances(
            appkey=args.appkey,
            account=args.account,
            password=args.password,
            appid=args.appid,
            networks=args.network,
        )
        for appliance in appliances:
            output(appliance, args.credentials)

    elif args.command == "status":
        if not args.token:
            if args.account and args.password:
                cloud = connect_to_cloud(
                    args.account, args.password, args.appkey, args.appid
                )
                appliance = appliance_state(args.ip, cloud=cloud)
            else:
                _LOGGER.error("Missing token/key or cloud credentials")
                return
        else:
            appliance = appliance_state(args.ip, token=args.token, key=args.key)
        if appliance is not None:
            output(appliance, args.credentials)
        else:
            _LOGGER.error("Unable to get appliance status %s", args.ip)

    elif args.command == "set":
        if not args.token:
            if args.account and args.password:
                cloud = connect_to_cloud(
                    args.account, args.password, args.appkey, args.appid
                )
                appliance = appliance_state(args.ip, cloud=cloud)
            else:
                _LOGGER.error("Missing token/key or cloud credentials")
                return
        else:
            appliance = appliance_state(args.ip, token=args.token, key=args.key)
        if appliance is not None:
            appliance.set_state(
                target_humidity=args.humidity,
                fan_speed=args.fan,
                mode=args.mode,
                ion_mode=args.ion,
                is_on=args.on,
            )
            output(appliance, args.credentials)


if __name__ == "__main__":
    cli()
