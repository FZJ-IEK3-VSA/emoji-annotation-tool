from colorful_emoji_annotations.utils.paths import STATIC_RESOURCES_DIR


# Load emojis from a file
with open(STATIC_RESOURCES_DIR / "emojis.txt", "r", encoding="utf-8") as f:
    EMOJIS = set(f.read().split(","))

def is_emoji(char: str) -> bool:
    """
    Check if given character is an emoji.
     
    Compares the character against a set of known emojis mainly compiled 
    from https://unicode.org/Public/emoji/latest/emoji-test.txt.    
    
    Args:
        char (str): Character to check.
    
    Returns:
        bool: True if character is an emoji, False otherwise.
    """
    return char in EMOJIS
