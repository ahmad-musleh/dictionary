import re
from django.db.models import Q

# Utility function to check for diacritics
def has_diacritics(text):
    return bool(re.search(r'[\u064B-\u0652]', text))

# Utility function to remove Arabic diacritics
def remove_diacritics(text):
    diacritics_pattern = re.compile(r'[\u0617-\u061A\u064B-\u0652]')
    return re.sub(diacritics_pattern, '', text)

# Utility function for spelling variations
def normalize_for_variations(text):
    """
    Generalizes Arabic text for handling spelling variations bidirectionally.
    Ensures variations like ة ↔ ه and ي ↔ ى are mutually interchangeable.
    """
    variations = {
        'إ': 'ا', 'أ': 'ا', 'ٱ': 'ا', 'آ': 'ا',  # Variants of Alif
        'ي': 'ى', 'ى': 'ي',                      # Variants of Alif Maqsura
        'ة': 'ه', 'ه': 'ة',                      # Variants of Ta Marbuta
        'ؤ': 'ء', 'ئ': 'ء', 'ء': 'ئ'             # Variants of Hamza
    }
    for char, replacement in variations.items():
        text = text.replace(char, replacement)
    return text

class QuerysetFilter:
    def __init__(self, queryset):
        self.queryset = queryset

    def apply_filters(self, filters):
        """
        Dynamically apply filters to a queryset based on provided dictionary of filters.
        """
        if not filters:
            return self.queryset

        q_filters = Q()
        # Dynamically apply valid filters
        for key, value in filters.items():
            if key == 'part_of_speech':
                q_filters &= Q(part_of_speech=value)
            elif key == 'scheme':
                q_filters &= Q(lemma__scheme=value)
            elif key == 'root':
                q_filters &= Q(
                    related_forms__targets=value,
                    related_forms__type='root'
                )
        return self.queryset.filter(q_filters).distinct()
