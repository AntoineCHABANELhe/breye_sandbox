from datetime import datetime as dtdt
from licensing.methods import Key, Helpers

from Source.BrailleTool.display import getDisplayString, Display
from Source.FilesHandling.environment_data import getKey, EnvironmentData

RSAPubKey = "<RSAKeyValue><Modulus>pXXB91vPtylvZGu4o2zdHjpCXXNa/NUSFXj4NRx2pnbw9HukgbVNxdDeSarL7O4CP2qvQhG2ioBymjfpn58tq3++AVB9gByU9IwLgbh9kZHmgvNdFT8Q+kQLsXYwP+coAFgLgZQzHHdGtOEH/vN83vPCTBW9MJV6wtFWND3tTkkgbWfN7dV12zUniM3p50RMnVguR+9pT1HL4AL3+zsLBOdILhCvtlZM7HZaJV34tNQaseXE/VkMv0DkzVI8jUQXOF9XJRIA3nN5+JCBjRD5PvHJaZ794Spptos5JpNNnSXs6MB6ttX5rAAkqWFkU5tzFFs22v6AyQ8LyRKTgL9/eQ==</Modulus><Exponent>AQAB</Exponent></RSAKeyValue>"


def authKey(key=""):
    result = Key.activate(token=EnvironmentData.AUTH.value, rsa_pub_key=RSAPubKey, product_id='25767', key=key or getKey(),
                          machine_code=Helpers.GetMachineCode(v=2))

    if result[0] is None or not Helpers.IsOnRightMachine(result[0], v=2):
        # an error occurred or the key is invalid, or it cannot be activated
        # (e.g. the limit of activated devices was achieved)
        dev = Key.activate(token=EnvironmentData.AUTH.value, rsa_pub_key=RSAPubKey, product_id='25396', key=key or getKey(),
                           machine_code=Helpers.GetMachineCode(v=2))

        if dev[0] is None or not Helpers.IsOnRightMachine(dev[0], v=2):
            return False, f"{result[1]}"  # Result here, not dev !
        else:
            if dtdt.now() > dev[0].expires:
                return False, getDisplayString(Display.DIS_KEY_EXPIRED)
            return True, ""
    else:
        if dtdt.now() > result[0].expires:
            return False, getDisplayString(Display.DIS_KEY_EXPIRED)
        return True, ""
