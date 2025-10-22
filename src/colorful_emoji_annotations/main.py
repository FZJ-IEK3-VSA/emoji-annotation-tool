
import re
import json
from collections import defaultdict, OrderedDict
from colorful_emoji_annotations.utils.paths import STATIC_RESOURCES_DIR
from colorful_emoji_annotations.utils.types import Annotations
from colorful_emoji_annotations.utils.emoji import is_emoji
try:
    from wasabi import Printer
    msg = Printer()
except ImportError:    
    msg = None    
    print("Warning: get_user_feedback() requires `wasabi' to be installed.")


class EmojiAnnotator:
    """
    A class to handle emoji annotations in text.

    Args:
        emoji_mapping (dict): A dictionary mapping labels to emojis. If None, default mapping is used.
    
    Attributes:
        - LABEL_EMOJI_MAPPING: A dictionary mapping labels to emojis.
        - EMOJI_LABEL_MAPPING: A dictionary mapping emojis to labels.
        - EMOJI_ANN_PATTERN: A regex pattern for matching emojis in text.

    Methods:
        - to_inline_annotations: Convert text and annotations into inline emoji-annotated text.
        - from_inline_annotations: Convert inline emoji-annotated text back to original text and annotations.
        - get_user_feedback: Get user feedback on the emoji mapping.
        - __len__: Get the number of concepts considered by the emoji mapping.
        - __getitem__: Get the emoji for a specific label.
        - __setitem__: Set the emoji for a specific label.
        - __delitem__: Delete an emoji mapping base on the label.

    """

    def __init__(self, emoji_mapping: dict = None):
        if emoji_mapping is None:
            # Load default emoji mapping from JSON file
            with open(STATIC_RESOURCES_DIR / "default_emoji_mapping.json", "r") as f:
                self.LABEL_EMOJI_MAPPING = json.load(f)                
        else:
            # Use passed emoji mapping
            self.LABEL_EMOJI_MAPPING = emoji_mapping
            
        self._validate_emoji_mapping(self.LABEL_EMOJI_MAPPING)
        self.EMOJI_LABEL_MAPPING = {v: k for k, v in self.LABEL_EMOJI_MAPPING.items()}
        self.EMOJI_ANN_PATTERN = re.compile("|".join(self.EMOJI_LABEL_MAPPING))
        self.EMOJIS_IN_MAPPING = list(self.LABEL_EMOJI_MAPPING.values())
    
    def __repr__(self):
        return f"EmojiAnnotations(emoji_mapping={self.LABEL_EMOJI_MAPPING})"
    
    def __str__(self):
        return f"EmojiAnnotations with mapping: {self.LABEL_EMOJI_MAPPING}"
    
    def __len__(self):
        """
        Count the number of concepts considered by the emoji mapping.
        """
        return len(self.LABEL_EMOJI_MAPPING)
    
    def __getitem__(self, key):
        """
        Get the emoji for a specific label.
        """
        if key in self.LABEL_EMOJI_MAPPING:
            return self.LABEL_EMOJI_MAPPING[key]
        else:
            raise KeyError(f"{key} not found in emoji mapping.")
    
    def __setitem__(self, key, value):
        """
        Set the emoji for a specific label.
        """
        self._validate_emoji_mapping({key: value})
        self.LABEL_EMOJI_MAPPING[key] = value        

    def __delitem__(self, key):
        """
        Delete an emoji mapping based on the label.
        """
        if key in self.LABEL_EMOJI_MAPPING:
            del self.LABEL_EMOJI_MAPPING[key]
        else:
            raise KeyError(f"{key} not found in emoji mapping.")

    def _validate_emoji_mapping(self, emoji_mapping):
        """
        Validate the emoji mapping dictionary.
        """
        if not isinstance(emoji_mapping, dict):
            raise ValueError("emoji_mapping must be a dictionary.")
        elif not all(isinstance(k, str) and isinstance(v, str) for k, v in emoji_mapping.items()):
            raise ValueError("emoji_mapping must contain string keys and values.")
        elif not all(is_emoji(v) for v in emoji_mapping.values()):
            raise ValueError("emoji_mapping must have a single emoji as values.")
        else:
            pass


    def to_inline_annotations(self, text: str, annotations: Annotations) -> str:
        """
        Transform text with annotations into inline emoji-annotated text.

        Note:
            If two emoji have the same character offset, the emoji that closes the active annotation
            is placed first. If the order was different in the original text, the order is not preserved 
            (e.g., "🏛️📍Louvre🏛️, Paris📍" would become "📍🏛️Louvre🏛️, Paris📍").

        Args:
            text (str): The text to annotate.
            annotations (Annotations): A dictionary of annotations, where the key is the 
                                      label or emoji and the value is a list of char offsets.

        Returns:
            str: The annotated text with emojis.

        Example:
            Args:            
                text = 'In 2023, life expectancy in europe was estimated at 81.4 years.'            
                annotations = {
                    'temporal_scope': [(3, 7)],
                    'property': [(9, 24)], 
                    'entity': [(28, 34)], 
                    'quantity': [(52, 56)], 
                    'unit': [(57, 62)]
                }
                
                Alternatively, you can use emojis instead of labels as keys:
                annotations = {
                    '📆': [(3, 7)], 
                    '🍊': [(9, 24)], 
                    '🌶️': [(28, 34)], 
                    '🍏': [(52, 56)], 
                    '🍓': [(57, 62)]
                }

            Returns:
                "In 📆2023📆, 🍊life expectancy🍊 in 🌶️Europe🌶️ was estimated at 🍏81.4🍏 🍓years🍓."
        """

        if all(label in list(self.LABEL_EMOJI_MAPPING) for label in list(annotations)):
            # If all labels are in the emoji mapping, use them as labels
            annotations = {self.LABEL_EMOJI_MAPPING[label]: offsets for label, offsets in annotations.items()}
        elif all(emoji in list(self.EMOJI_LABEL_MAPPING) for emoji in list(annotations)):
            pass 
        else:
            # If not all labels are in the emoji mapping, raise an error
            raise ValueError(f"Annotation '{annotations}' dict includes concepts that are not part of the emoji mapping: {self.LABEL_EMOJI_MAPPING}")    

        ann_offsets_with_tags = []
        for tag, ann in annotations.items():
            ann_offsets = list(sum(ann, ()))
            ann_offsets_with_tags += [(offset, tag) for offset in ann_offsets]

        # Get tag order for grouping by tag
        ann_offsets_with_tags = sorted(ann_offsets_with_tags, key=lambda x: x[0])
        tag_order = list(OrderedDict.fromkeys([t[1] for t in ann_offsets_with_tags]))

        # Sort from large to small whilst ensuring that
        # annotations are grouped by their tag
        ann_offsets_with_tags = sorted(
            ann_offsets_with_tags,
            key=lambda x: (x[0], tag_order.index(x[1])),
            reverse=True,
        )

        # Annotate sentence
        text_ann = text
        last_tag = None
        last_offset = None
        switched_tag_pos = False
        for (curr_offset, curr_tag), (next_offset, next_tag) in zip(ann_offsets_with_tags[:-1], ann_offsets_with_tags[1:]):

            if switched_tag_pos:
                # Use last tag and offset because the current 
                # ones were already used.
                offset = last_offset
                tag = last_tag
                switched_tag_pos = False
            elif curr_offset == next_offset and last_tag == next_tag:
                # Two tags have the same character offset. Use the tag that
                # closes the active annotation first.                
                switched_tag_pos = True
                offset = next_offset
                tag = next_tag                
            else:
                # Insert current tag.
                offset = curr_offset
                tag = curr_tag
                                 
            text_ann = text_ann[:offset] + tag + text_ann[offset:]

            last_tag = curr_tag
            last_offset = curr_offset

        # Insert last tag
        if switched_tag_pos:
            next_offset, next_tag = ann_offsets_with_tags[-2]
        
        text_ann = text_ann[:next_offset] + next_tag + text_ann[next_offset:]

        return text_ann


    def from_inline_annotations(self, annotated_text: str, emojis_as_keys: bool=False) -> tuple[str, Annotations]:
        """
        Transform inline emoji-annotated text into plain text and annotations.
        
        Args:
            annotated_text (str): The annotated text with emojis.
            emojis_as_keys (bool): If True, use emojis as keys in the annotations dictionary.
        
        Returns:
            plain_text (str): The plain text without annotations.
            annotations (Annotations): A dictionary of annotations, where the key is the label or emoji and the value is a list of char offsets.
        """

        # Get annotations as flat list of char offsets.
        offset = 0
        flat_annotations = defaultdict(list)
        for match in self.EMOJI_ANN_PATTERN.finditer(annotated_text):
            symbol = match.group()
            tag = self.EMOJI_LABEL_MAPPING.get(symbol)
            if tag is None:
                raise ValueError("Missing annotation mapping.")
            else:
                flat_annotations[tag].append(match.start() - offset)
                offset += len(symbol)

        # Create a list of (start, end) char offsets for each annotation.
        annotations = defaultdict(list)
        for label, pos in flat_annotations.items():
            if len(pos) % 2 != 0:
                raise ValueError(f"An annotation is not properly closed in '{annotated_text}'")
            else:
                key = self.LABEL_EMOJI_MAPPING[label] if emojis_as_keys else label
                for i in range(0, len(pos), 2):                    
                    annotations[key].append((pos[i], pos[i + 1]))
        
        # Remove all emojis from the text.
        plain_text = self.EMOJI_ANN_PATTERN.sub("", annotated_text)

        return plain_text, dict(annotations) # defaultdict to dict


    def get_user_feedback(
        self,        
        annotated_text: str,
        text_color: str = "cyan",
        cmd_help_color: str = "pink",
        active_ann_symbol: str = "🔻",
    ) -> tuple[Annotations, str, bool]:
        """
        Get user feedback on the annotated text.
        
        The user can mark the example as correct or incorrect by pressing 'y' or 'n'.
        If the example is incorrect, the user can correct the annotations by moving the 
        annotation boundaries with the arrow keys or delete all annotation by pressing 'd'.

        Args:
            annotated_text (str): The annotated text with emojis.
            text_color (str, optional): The color of the text.
            cmd_help_color (str, optional): The color of the command help text.
            active_ann_symbol (str, optional): The symbol used to indicate the active annotation boundary.
        
        Returns:
            annotated_text (str): The modified inline emoji-annotated text.
            correct (bool): True if the example was marked as correct, False otherwise.
        """
        
        emoji_count = len(self.EMOJI_ANN_PATTERN.findall(annotated_text))
        allowed_idx_keys = [str(i) for i in range(1, emoji_count + 1)]

        msg.text("Computer says 🗯️", color="grey")
        msg.text(annotated_text, spaced=True, color=text_color)
        msg.text("Correct? y/n", color=cmd_help_color)
        msg.text("(To edit the n-th annotation, enter its number n, e.g. '3', press enter, "\
                 "use the arrow keys to move it, press enter to see the changes, and press enter "\
                 "again to confirm the changes. To delete all annotations press 'd'.)", color=cmd_help_color)
        left = "\x1b[D"
        right = "\x1b[C"
        emoji_idx = None
        while True:
            key = input()
            if key == "":
                msg.text(annotated_text, spaced=True, color=text_color)
                msg.text("Correct? y/n", color=cmd_help_color)
            elif key in allowed_idx_keys:
                # Select an annotation boundary.
                emoji_idx = int(key) - 1
                emoji_matches = list(self.EMOJI_ANN_PATTERN.finditer(annotated_text))                
                sent_w_active_emoji = (
                    annotated_text[: emoji_matches[emoji_idx].start()]
                    + active_ann_symbol
                    + annotated_text[emoji_matches[emoji_idx].end() :]
                )
                msg.text(sent_w_active_emoji, spaced=True, color=text_color)
                target_symbol = emoji_matches[emoji_idx].span()
            elif key in ["y", "n"]:
                # Mark example as correct or incorrect.
                correct = True if key == "y" else False
                break
            elif emoji_idx != None and (
                all(r == "" for r in key.split(right))
                or all(l == "" for l in key.split(left))
            ):
                # Move selected annotation boundary left or right.
                right_keys = len(key.split(right))
                left_keys = len(key.split(left))
                offset = right_keys - left_keys
                symbol = annotated_text[target_symbol[0] : target_symbol[1]]
                annotated_text = annotated_text[: target_symbol[0]] + annotated_text[target_symbol[1] :]
                target_symbol = (target_symbol[0] + offset, target_symbol[1] + offset)
                insert_at = target_symbol[0]
                annotated_text = annotated_text[:insert_at] + active_ann_symbol + annotated_text[insert_at:]
                msg.text(annotated_text, spaced=True, color=text_color)
                msg.text("Correct? y/n", color=cmd_help_color)
                annotated_text = annotated_text.replace(active_ann_symbol, symbol)
            elif key == "d":
                # Delete all annotations.
                annotated_text = self.EMOJI_ANN_PATTERN.sub("", annotated_text)
                msg.text(annotated_text, spaced=True, color=text_color)
                msg.text("Correct? y/n", color=cmd_help_color)
            else:
                # Play by the rules!
                msg.warn("Enter 'y' or 'n'. Another try:")        

        return annotated_text, correct