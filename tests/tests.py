from pathlib import Path
from colorful_emoji_annotations import EmojiAnnotator
from colorful_emoji_annotations.utils.emoji import is_emoji


def test_create_emoji_annotation_object(emoji_mapping):
    """
    Test the creation of the EmojiAnnotation object.
    """
    emoji_nlp = EmojiAnnotator(emoji_mapping)
    assert emoji_nlp.LABEL_EMOJI_MAPPING == emoji_mapping
    return emoji_nlp


def test_is_emoji():
    """
    Test the is_emoji function.
    """    
    emoji_file = Path(__file__).parent / "test_emojis.txt"
    with open(emoji_file, "r") as f:
        emojis = f.read().split(",")

    for emoji in emojis:
        assert is_emoji(emoji), f"Failed to recognize emoji: {emoji}"    

    for char in 'pÄèl/P:ehm6ÖYf&.²jycB§,[4oé+xi)dH(`*váXÜa$OFQK{;-J8#³S\\!UE´Ck]%zßWD}2w?3At5nZ0TLr9àäRsMI1êâü_GNö7<Vqgu"^b=©️,®️,‼️,⁉️,™️,ℹ️,↔️,↕️,▪️,▫️,':
        assert not is_emoji(char), f"Failed to recognize non-emoji character: {char}"


def test_get_set_del_emojis(emoji_nlp):
    """
    Test the get, set, and delete emojis.
    """    
    
    # Test getting emojis.
    assert emoji_nlp["quantity"] == "🍏"
    
    # Test setting emojis.
    emoji_nlp["rat"] = "🐀"
    assert emoji_nlp["rat"] == "🐀"
    
    # Test deleting emojis.
    del emoji_nlp["rat"]
    assert "rat" not in emoji_nlp.LABEL_EMOJI_MAPPING


def test_from_inline_annotations_to_annotated_text(emoji_nlp):
    """
    Test the conversion of inline tags to char offsets.
    """
    
    example = "🌶️Andalusia🌶️ has a 🍊surface area🍊 of 🍏87,597🍏 🍓square kilometres🍓.   "

    # Test the conversion from annotated text to char offsets.
    plain_text, annotations = emoji_nlp.from_inline_annotations(example)
    assert annotations == {'entity': [(0, 9)], 'property': [(16, 28)], 'quantity': [(32, 38)], 'unit': [(39, 56)]}
    assert plain_text == "Andalusia has a surface area of 87,597 square kilometres.   "

    # Test the reverse conversion.
    example_ = emoji_nlp.to_inline_annotations(plain_text, annotations)
    assert example_ == example

    # Test the reverse conversion with emojis instead of labels as keys in annotations.
    annotations_ = {emoji_nlp.LABEL_EMOJI_MAPPING.get(k): v for k, v in annotations.items()}
    example_ = emoji_nlp.to_inline_annotations(plain_text, annotations_)
    assert example_ == example


def test_user_feedback(emoji_nlp):
    """
    Test the user feedback functionality.
    Note: This part requires manual testing as it involves user interaction.
    """

    example = "🌶️Andalusia🌶️ has a 🍊surface area🍊 of 🍏87,597🍏 🍓square kilometres🍓."             
    curated_example, correct = emoji_nlp.get_user_feedback(example)
    # ...
    

if __name__ == "__main__":

    EMOJI_MAPPING = {
        "entity": "🌶️",
        "property": "🍊",
        "quantity": "🍏",
        "unit": "🍓",
        "temporal_scope": "📆",
    }
    
    test_is_emoji()
    emoji_nlp = test_create_emoji_annotation_object(EMOJI_MAPPING)
    test_get_set_del_emojis(emoji_nlp)
    test_from_inline_annotations_to_annotated_text(emoji_nlp)
    test_user_feedback(emoji_nlp)
    
    print("✅ All tests passed.")

