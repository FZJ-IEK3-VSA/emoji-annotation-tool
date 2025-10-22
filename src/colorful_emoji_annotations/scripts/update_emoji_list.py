# This script extracts emojis from the Unicode emoji-test.txt file and saves them to a text file.
import re
import urllib.request


# Get the latest version of the emoji-test.txt file from Unicode's website.
url = "https://unicode.org/Public/emoji/latest/emoji-test.txt"
unicode_emoji_file = urllib.request.urlopen(url).read()
unicode_emoji_file_lines = unicode_emoji_file.decode("utf-8").splitlines()

# Extract emojis.
emojis = []
EMOJI_PATTERN = re.compile(r"#\s([^\s]+)\sE")
for line in unicode_emoji_file_lines:
    if line.startswith("#") or len(line.strip()) == 0:        
        # Comment or empty line.
        continue
    elif "; unqualified " in line:
        # Skip unqualified emojis.
        continue
    else:
        # Data line. Extract the emoji from the line.        
        match = EMOJI_PATTERN.search(line)
        if match:        
            emojis.append(match.group(1))            
        else:
            raise ValueError(f"Could not find emoji in line: {line}")

# Add known emojis that are not in the emoji-test.txt file but considered here.
additional_emojis = ['⌚️', '⌛️', '⏩️', '⏪️', '⏫️', '⏬️', '⏰️', '⏳️', '◽️', '◾️', '☔️', '☕️', '♈️', '♉️', '♊️', '♋️', '♌️', '♍️', '♎️', '♏️', '♐️', '♑️', '♒️', '♓️', '♿️', '⚓️', '⚡️', '⚪️', '⚫️', '⚽️', '⚾️', '⛄️', '⛅️', '⛎️', '⛔️', '⛪️', '⛲️', '⛳️', '⛵️', '⛺️', '⛽️', '✅️', '✊️', '✋️', '✨️', '❌️', '❎️', '❓️', '❔️', '❕️', '❗️', '➕️', '➖️', '➗️', '➰️', '➿️', '⬛️', '⬜️', '⭐️', '⭕️']
emojis.extend(additional_emojis)

# Save emojis to text file.
with open("src/emoji_annotations/static_resources/emojis.txt", "w", encoding="utf-8") as f:
    f.write(",".join(emojis))

print(f"✅ Successfully updated emojis.txt file. In total {len(emojis)} emojis were extracted.")