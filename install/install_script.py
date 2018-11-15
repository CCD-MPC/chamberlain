import sys

from install import ConclaveWebInstaller

if len(sys.argv) > 1:
    swift_param = sys.argv[1]
else:
    swift_param = True

installer = ConclaveWebInstaller(with_swift=swift_param)
installer.launch_all()