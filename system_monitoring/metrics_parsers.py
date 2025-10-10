def parse_percent(value):
    stripped_value = str(value).strip()
    if stripped_value.endswith("%"):  # в условии нет знака процента для cpu
        stripped_value = stripped_value[:-1]
    float_value = float(stripped_value)
    if float_value < 0 or float_value > 100:
        raise ValueError(f"Percent {float_value} out of range")
    return int(float_value)


def parse_uptime(text):
    stripped_text = str(text).strip().lower()
    if not stripped_text:
        raise ValueError(f"Invalid uptime: {text}")
    total = 0
    values = {"d": 86400, "h": 3600, "m": 60, "s": 1}  # в секундах
    quantity_beetween_values = ""

    for char in stripped_text:
        if char.isdigit():
            quantity_beetween_values += char
            continue
        if char.isspace():
            continue
        if char in values:
            if not quantity_beetween_values:
                raise ValueError(f"No number before uptime value: {char}")
            total += int(quantity_beetween_values) * values[char]
            quantity_beetween_values = ""
            continue
        raise ValueError(f"Invalid character: {char}")
    if quantity_beetween_values:
        raise ValueError(
            f"Number without uptime value: {quantity_beetween_values}"
        )
    return total
