def sanitize_filename(filename: str) -> str:
    output = ""
    for char in filename:
        if char in '"*:<>?|/\\':
            char = {'/': '\u29F8', '\\': '\u29f9'}.get(char, chr(ord(char) + 0xfee0))
        output += char
    return output
