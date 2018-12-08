import argparse

from install import ConclaveWebInstaller


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Install C2D on OpenShift")
    parser.add_argument("--swift", type=bool, default=False, required=False)
    parser.add_argument("--dv", type=bool, default=False, required=False)
    parser.add_argument("--vol", type=bool, default=False, required=False)

    args = parser.parse_args()

    installer = ConclaveWebInstaller(with_swift=args.swift, with_dv=args.dv, with_vol=args.vol)
    installer.launch_all()
