import xml.etree.ElementTree as ET
import os
import django

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "your_project.settings")
django.setup()

from dictionary.models import LexicalEntry, Lemma, WordForm, RelatedForm, Sense, Definition, Context, SyntacticBehaviour

def parse_lmf_xml(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()

    lexical_entries = []
    lemmas = []
    word_forms = []
    related_forms = []
    senses = []
    definitions = []
    contexts = []
    syntactic_behaviours = []

    for lexical_entry_element in root.findall('LexicalEntry'):
        # Create LexicalEntry
        entry_id = lexical_entry_element.get('id', '')
        part_of_speech_element = lexical_entry_element.find("feat[@att='partOfSpeech']")
        if part_of_speech_element is None or not part_of_speech_element.get('val', '').strip():
            raise ValueError("PartOfSpeech is required and cannot be null or empty.")
        part_of_speech = part_of_speech_element.get('val', '').strip()
        lexical_entry = LexicalEntry(id=entry_id, part_of_speech=part_of_speech)
        lexical_entries.append(lexical_entry)

        # Create Lemma
        lemma_element = lexical_entry_element.find('Lemma')
        if lemma_element is not None:
            written_form = ''
            scheme = None
            written_form_element = lemma_element.find("feat[@att='writtenForm']")
            if written_form_element is not None:
                written_form = written_form_element.get('val', '')
            scheme_element = lemma_element.find("feat[@att='Scheme']")
            if scheme_element is not None:
                scheme = scheme_element.get('val', None)
            lemmas.append(Lemma(lexical_entry=lexical_entry, written_form=written_form, scheme=scheme))

        # Create WordForms
        for word_form_element in lexical_entry_element.findall('WordForm'):
            written_form = ''
            grammatical_number = None
            grammatical_gender = None
            tense = None
            person = None
            grammatical_voice = None

            written_form_element = word_form_element.find("feat[@att='writtenForm']")
            if written_form_element is not None:
                written_form = written_form_element.get('val', '')

            grammatical_number_element = word_form_element.find("feat[@att='GrammaticalNumber']")
            if grammatical_number_element is not None:
                grammatical_number = grammatical_number_element.get('val', None)

            grammatical_gender_element = word_form_element.find("feat[@att='GrammaticalGender']")
            if grammatical_gender_element is not None:
                grammatical_gender = grammatical_gender_element.get('val', None)

            tense_element = word_form_element.find("feat[@att='tense']")
            if tense_element is not None:
                tense = tense_element.get('val', None)

            person_element = word_form_element.find("feat[@att='Person']")  # Updated case
            if person_element is not None:
                person = person_element.get('val', None)

            grammatical_voice_element = word_form_element.find("feat[@att='GrammaticalVoice']")  # Updated case
            if grammatical_voice_element is not None:
                grammatical_voice = grammatical_voice_element.get('val', None)

            word_forms.append(
                WordForm(
                    lexical_entry=lexical_entry,
                    written_form=written_form,
                    grammatical_number=grammatical_number,
                    grammatical_gender=grammatical_gender,
                    tense=tense,
                    person=person,
                    grammatical_voice=grammatical_voice
                )
            )


        # Create RelatedForms
        for related_form_element in lexical_entry_element.findall('RelatedForm'):
            targets = related_form_element.get('targets', '')
            type_val = None
            type_element = related_form_element.find("feat[@att='type']")
            if type_element is not None:
                type_val = type_element.get('val', '')
            related_forms.append(
                RelatedForm(
                    lexical_entry=lexical_entry,
                    targets=targets,
                    type=type_val
                )
            )

        # Create Senses
        for sense_element in lexical_entry_element.findall('Sense'):
            sense_id = sense_element.get('id', '')
            sense = Sense(lexical_entry=lexical_entry, id=sense_id)
            senses.append(sense)

            for definition_element in sense_element.findall('Definition'):
                text = ''
                text_element = definition_element.find("feat[@att='text']")
                if text_element is not None:
                    text = text_element.get('val', '')
                definitions.append(Definition(sense=sense, text=text))

            for context_element in sense_element.findall('Context'):
                text = ''
                text_element = context_element.find("feat[@att='text']")
                if text_element is not None:
                    text = text_element.get('val', '')
                contexts.append(Context(sense=sense, text=text))

        # Create SyntacticBehaviours
        for syntactic_behaviour_element in lexical_entry_element.findall('SyntacticBehaviour'):
            subcategorization_frames = syntactic_behaviour_element.get('subcategorizationFrames', '')
            syntactic_behaviours.append(
                SyntacticBehaviour(
                    lexical_entry=lexical_entry,
                    subcategorization_frames=subcategorization_frames
                )
            )

    # Bulk create in the database
    LexicalEntry.objects.bulk_create(lexical_entries, batch_size=1000)
    Lemma.objects.bulk_create(lemmas, batch_size=1000)
    WordForm.objects.bulk_create(word_forms, batch_size=1000)
    RelatedForm.objects.bulk_create(related_forms, batch_size=1000)
    Sense.objects.bulk_create(senses, batch_size=1000)
    Definition.objects.bulk_create(definitions, batch_size=1000)
    Context.objects.bulk_create(contexts, batch_size=1000)
    SyntacticBehaviour.objects.bulk_create(syntactic_behaviours, batch_size=1000)

def main():
    xml_file = "corrected_LMF-ArDict.xml"  # Replace with the path to your LMF XML file
    parse_lmf_xml(xml_file)
    print("Database populated successfully!")

if __name__ == "__main__":
    main()