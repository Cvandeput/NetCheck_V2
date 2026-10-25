def int_to_bin(value: int) -> str:
    if value == 0:
        return "00000000"
        
    bits = []
    while value > 0:
        reste = value % 2
        bits.append(str(reste))
        value = value // 2 
        
    bits.reverse()
    
    resultat = "".join(bits)
    return resultat.zfill(8)


def bin_to_int(text: str) -> int | None:
    if type(text) is not str or text == "":
        return None

    value = 0
    text_inverse = reversed(text)
    
    for i, char in enumerate(text_inverse):
        if char not in ("0", "1"):
            return None
            
        if char == "1":
            value += 2 ** i
            
    return value


def remove_spaces(text: str) -> str:
    if type(text) is not str:
        return ""

    return "".join(text.split())
