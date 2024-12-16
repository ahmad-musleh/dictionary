from rest_framework.serializers import ModelSerializer
from .models import LexicalEntry, Lemma, WordForm, RelatedForm, Sense, Definition, Context, SyntacticBehaviour
from rest_framework import serializers

class DefinitionSerializer(ModelSerializer):
    class Meta:
        model = Definition
        fields = ['text']

class ContextSerializer(ModelSerializer):
    class Meta:
        model = Context
        fields = ['text']

class SenseSerializer(ModelSerializer):
    definitions = DefinitionSerializer(many=True)
    contexts = ContextSerializer(many=True)

    class Meta:
        model = Sense
        fields = ['id', 'definitions', 'contexts']

class LemmaSerializer(ModelSerializer):
    class Meta:
        model = Lemma
        fields = ['written_form', 'scheme']

class WordFormSerializer(ModelSerializer):
    class Meta:
        model = WordForm
        fields = ['written_form', 'grammatical_number', 'grammatical_gender', 'tense', 'person', 'grammatical_voice']

class RelatedFormSerializer(ModelSerializer):
    class Meta:
        model = RelatedForm
        fields = ['targets', 'type']

class SyntacticBehaviourSerializer(ModelSerializer):
    class Meta:
        model = SyntacticBehaviour
        fields = ['subcategorization_frames']

class LexicalEntrySerializer(ModelSerializer):
    lemma = LemmaSerializer()
    word_forms = WordFormSerializer(many=True)
    related_forms = RelatedFormSerializer(many=True)
    senses = SenseSerializer(many=True)
    syntactic_behaviours = SyntacticBehaviourSerializer(many=True)

    class Meta:
        model = LexicalEntry
        fields = ['id', 'part_of_speech', 'lemma', 'word_forms', 'related_forms', 'senses', 'syntactic_behaviours']


class PhraseSearchQuerySerializer(serializers.Serializer):
    query = serializers.CharField(required=True, help_text="The word or phrase to search for in definitions and contexts (e.g., في الجَرِيرة، تَشْترك العَشيرة)")
    part_of_speech = serializers.CharField(required=False, help_text="Filter by part of speech.")
    scheme = serializers.CharField(required=False, help_text="Filter by scheme.")
    root = serializers.CharField(required=False, help_text="Filter by root.")
    page = serializers.IntegerField(required=False, help_text="Page number for pagination.")
    page_size = serializers.IntegerField(required=False, help_text="Number of results per page.")

class RootSearchQuerySerializer(serializers.Serializer):
    root = serializers.CharField(required=True, help_text="The root to search for (e.g., كتب).")
    part_of_speech = serializers.CharField(required=False, help_text="Filter by part of speech.")
    scheme = serializers.CharField(required=False, help_text="Filter by scheme.")
    page = serializers.IntegerField(required=False, help_text="Page number for pagination.")
    page_size = serializers.IntegerField(required=False, help_text="Number of results per page.")

class DictionaryRetrieveQuerySerializer(serializers.Serializer):
    query = serializers.CharField(required=True, help_text="The word to search for, with or without diacritics (e.g., كُتُب).")
    part_of_speech = serializers.CharField(required=False, help_text="Filter by part of speech.")
    scheme = serializers.CharField(required=False, help_text="Filter by scheme.")
    root = serializers.CharField(required=False, help_text="Filter by root.")
    page = serializers.IntegerField(required=False, help_text="Page number for pagination.")
    page_size = serializers.IntegerField(required=False, help_text="Number of results per page.")
