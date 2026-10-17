from enum import Enum
from .utils import bin_to_int, int_to_bin

class ClassMask(Enum):
    CLASS_A = "255.0.0.0"
    CLASS_B = "255.255.0.0"
    CLASS_C = "255.255.255.0"
    CLASS_D = "N/A_D"
    CLASS_E = "N/A_E"
    ERROR = "error"

# --- verification si ip correcte ---
def isIp(ip: str) -> bool:
    if type(ip) is not str:
        return False

    parts = ip.split(".")
    if len(parts) != 4:
        return False

    for part in parts:
        if not part.isdigit():
            return False

        value = int(part)
        if value is None or value < 0 or value > 255:
            return False

    return True

# --- Analyse masque ---
def parseMask(mask: str) -> str | None:
    if type(mask) is not str:
        return None

    cleaned = mask.strip()
    if cleaned.startswith("/"):
        cleaned = cleaned[1:]

    if cleaned.isdigit():
        cidr = int(cleaned)
        if cidr is None or cidr < 0 or cidr > 32:
            return None
        return _cidrToMask(cidr)

    if isIp(cleaned):
        return cleaned

    return None

def _cidrToMask(cidr: int) -> str:
    bits = "1" * cidr + "0" * (32 - cidr)
    octets = []

    for i in range(0, 32, 8):
        value = bin_to_int(bits[i:i + 8])
        octets.append(str(value))

    return ".".join(octets)

def isSubnetMask(mask: str) -> bool:
    normalized = parseMask(mask)
    if not normalized:
        return False

    bits = []
    for part in normalized.split("."):
        value = int(part)
        if value is None:
            return False
        bits.append(int_to_bin(value))

    return "01" not in "".join(bits)

def getNetworkAddress(ip: str, mask: str) -> str:
    normalized = parseMask(mask)
    if not isIp(ip) or not normalized:
        return ClassMask.ERROR.value

    ip_parts = ip.split(".")
    mask_parts = normalized.split(".")

    result_parts = []
    for i in range(4):
        ip_value = int(ip_parts[i])
        mask_value = int(mask_parts[i])
        if ip_value is None or mask_value is None:
            return ClassMask.ERROR.value

        ip_bin = int_to_bin(ip_value)
        mask_bin = int_to_bin(mask_value)

        and_bits = []
        for j in range(8):
            if ip_bin[j] == "1" and mask_bin[j] == "1":
                and_bits.append("1")
            else:
                and_bits.append("0")

        and_value = bin_to_int("".join(and_bits))
        result_parts.append(str(and_value))

    return ".".join(result_parts)

def getIPClass(ip: str) -> ClassMask:
    if not isIp(ip):
        return ClassMask.ERROR

    firstNum = int(ip.split(".")[0])

    if 0 <= firstNum <= 127:
        return ClassMask.CLASS_A
    elif 128 <= firstNum <= 191:
        return ClassMask.CLASS_B
    elif 192 <= firstNum <= 223:
        return ClassMask.CLASS_C
    elif 224 <= firstNum <= 239:
        return ClassMask.CLASS_D
    elif 240 <= firstNum <= 255:
        return ClassMask.CLASS_E

    return ClassMask.ERROR





def isClassFull(mask: str) -> bool:
    normalized = parseMask(mask)
    if not normalized:
        return False

    return normalized in {
        ClassMask.CLASS_A.value,
        ClassMask.CLASS_B.value,
        ClassMask.CLASS_C.value,
    }


def isPrivateIp(ip: str) -> bool:
    if not isIp(ip):
        return False

    parts = ip.split(".")
    first = int(parts[0])
    second = int(parts[1])

    if first == 10:
        return True

    if first == 172 and 16 <= second <= 31:
        return True

    if first == 192 and second == 168:
        return True

    return False


def isReservedIp(ip: str) -> bool:
    if not isIp(ip):
        return False

    if ip == "0.0.0.0":
        return True

    if ip == "255.255.255.255":
        return True

    first = int(ip.split(".")[0])
    second = int(ip.split(".")[1])

    if first == 0:
        return True

    if first == 127:
        return True

    if first == 169 and second == 254:
        return True

    if 224 <= first <= 239:
        return True

    if 240 <= first <= 255:
        return True

    return False


def getIPClassMask(ip: str) -> str:
    if not isIp(ip):
        return ClassMask.ERROR.value

    ipClasse = getIPClass(ip)

    match ipClasse:
        case ClassMask.CLASS_A | ClassMask.CLASS_B | ClassMask.CLASS_C:
            return ipClasse.value
        case ClassMask.CLASS_D | ClassMask.CLASS_E:
            return "N/A"
        case _:
            return ClassMask.ERROR.value


def getSubnet(ip: str, mask: str) -> str:
    normalized = parseMask(mask)
    if not isIp(ip) or not normalized:
        return ClassMask.ERROR.value

    if not isSubnetMask(normalized):
        return ClassMask.ERROR.value

    return getNetworkAddress(ip, normalized)


def areIpsInSameNetwork(ip1: str, mask1: str, ip2: str, mask2: str) -> bool:
    if not isIp(ip1) or not isIp(ip2):
        return False

    normalized_1 = parseMask(mask1)
    normalized_2 = parseMask(mask2)
    if not normalized_1 or not normalized_2:
        return False

    if not isSubnetMask(normalized_1) or not isSubnetMask(normalized_2):
        return False

    network_from_1 = getNetworkAddress(ip1, normalized_1)
    network_from_2 = getNetworkAddress(ip2, normalized_2)

    if network_from_1 == ClassMask.ERROR.value or network_from_2 == ClassMask.ERROR.value:
        return False

    return (
        getNetworkAddress(ip1, normalized_1) == getNetworkAddress(ip2, normalized_1)
        and getNetworkAddress(ip2, normalized_2) == getNetworkAddress(ip1, normalized_2)
    )


def genererTableauCIDR() -> list[list[str]]:
    tableResult = []
    for cidr in range(8, 31):
        line = []

        binaires = "1" * cidr + "0" * (32 - cidr)
        octets_binaires = []

        for i in range(0, 32, 8):
            octets_binaires.append(binaires[i:i + 8])

        binaire_pointe = ".".join(octets_binaires)

        decimal = []
        for octet in octets_binaires:
            decimal.append(str(bin_to_int(octet)))

        decimal_pointe = ".".join(decimal)

        line.append(f"{cidr}")
        line.append(binaire_pointe)
        line.append(decimal_pointe)

        tableResult.append(line)

    return tableResult


# --- Division d'un reseau en sous-reseaux ---

# --- conversion masque -> CIDR (ex: 255.255.255.0 -> 24), inverse de _cidrToMask ---
def maskToCidr(mask: str) -> int | None:
    normalized = parseMask(mask)
    if not normalized or not isSubnetMask(normalized):
        return None

    # le CIDR = nombre de bits a 1 dans le masque
    cidr = 0
    for part in normalized.split("."):
        cidr += int_to_bin(int(part)).count("1")

    return cidr

# --- conversion IP -> entier 32 bits (pour pouvoir additionner le pas) ---
def _ipToInt(ip: str) -> int | None:
    if not isIp(ip):
        return None

    # on colle les 4 octets en binaire puis on convertit les 32 bits en entier
    bits = []
    for part in ip.split("."):
        bits.append(int_to_bin(int(part)))

    return bin_to_int("".join(bits))

# --- conversion entier 32 bits -> IP ---
def _intToIp(value: int) -> str:
    # on complete a 32 bits puis on recoupe en 4 octets de 8 bits
    bits = int_to_bin(value).zfill(32)
    octets = []

    for i in range(0, 32, 8):
        octets.append(str(bin_to_int(bits[i:i + 8])))

    return ".".join(octets)

# --- etape 2 : on cherche n pour que 2^n >= nombre de sous-reseaux ---
def getSubnetBits(number_subnet: int) -> int:
    n = 0
    while 2 ** n < number_subnet:
        n += 1

    return n

# --- etape 3/4 : pas entre deux IP reseau = 2^(32 - CIDR) (ex: 2^6 = 64 = 62 IP utilisables + 2) ---
def getSubnetStep(cidr: int) -> int:
    # 2^(32 - CIDR) = IP utilisables + adresse reseau + adresse broadcast
    return 2 ** (32 - cidr)

# --- affichage : N° | IP reseau | IP broadcast | 1ere IP | derniere IP ---
def divideSubnetwork(ip: str, mask: str, number_subnet: int, new_cidr: int) -> list[list[str]]:
    network = getNetworkAddress(ip, mask)
    if network == ClassMask.ERROR.value:
        return []

    step = getSubnetStep(new_cidr)

    # on part de l'adresse reseau (au cas ou l'utilisateur donne une IP d'hote)
    network_value = _ipToInt(network)

    tableResult = []
    for i in range(number_subnet):
        line = []

        # chaque sous-reseau commence un pas plus loin que le precedent
        subnet_value = network_value + i * step
        broadcast_value = subnet_value + step - 1

        line.append(f"{i + 1}")
        line.append(_intToIp(subnet_value))
        line.append(_intToIp(broadcast_value))
        line.append(_intToIp(subnet_value + 1))
        line.append(_intToIp(broadcast_value - 1))

        tableResult.append(line)

    return tableResult
