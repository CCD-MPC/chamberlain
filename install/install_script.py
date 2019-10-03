import argparse

from install import ChamberlainInstaller


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Install C2D on OpenShift")
    parser.add_argument("--swift", type=bool, default=False, required=False)
    parser.add_argument("--dv", type=bool, default=False, required=False)
    parser.add_argument("--vol", type=bool, default=False, required=False)
    parser.add_argument("--mini", type=bool, default=False, required=False)
    parser.add_argument("--client_install", type=bool, default=False, required=False)

    args = parser.parse_args()

    installer = ChamberlainInstaller(with_swift=args.swift, with_dv=args.dv, with_vol=args.vol, minishift=args.mini)

    if not args.client_install:
        installer.build_chamberlain_server()
    else:
        installer.build_chamberlain_client()
