import re
import unicodedata

def slugify(value):
    """
    Converts a string into a slug: lowercase, hyphen-separated, no special characters.
    Example: "Data Types & Variables" → "data-types-variables"
    """
    value = str(value)
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^\w\s-]', '', value).strip().lower()
    value = re.sub(r'[-\s]+', '-', value)
    return value

