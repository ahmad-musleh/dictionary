from django.db import models

class LexicalEntry(models.Model):
    auto_id = models.AutoField(primary_key=True)
    id = models.CharField(max_length=50)
    part_of_speech = models.CharField(max_length=50, db_index=True)  # Indexed

class Lemma(models.Model):
    lexical_entry = models.OneToOneField(LexicalEntry, on_delete=models.CASCADE, related_name="lemma")
    written_form = models.CharField(max_length=255, db_index=True)  # Indexed
    scheme = models.CharField(max_length=255, null=True, blank=True, db_index=True)  # Indexed

class WordForm(models.Model):
    lexical_entry = models.ForeignKey(LexicalEntry, on_delete=models.CASCADE, related_name="word_forms")
    written_form = models.CharField(max_length=255, db_index=True)  # Indexed
    grammatical_number = models.CharField(max_length=50, null=True, blank=True, db_index=True)  # Indexed
    grammatical_gender = models.CharField(max_length=50, null=True, blank=True, db_index=True)  # Indexed
    tense = models.CharField(max_length=50, null=True, blank=True, db_index=True)  # Indexed
    person = models.CharField(max_length=50, null=True, blank=True)
    grammatical_voice = models.CharField(max_length=50, null=True, blank=True)

class RelatedForm(models.Model):
    lexical_entry = models.ForeignKey(LexicalEntry, on_delete=models.CASCADE, related_name="related_forms")
    targets = models.CharField(max_length=255, db_index=True)  # Indexed
    type = models.CharField(max_length=50, db_index=True)  # Indexed

class Sense(models.Model):
    auto_id = models.AutoField(primary_key=True)
    id = models.CharField(max_length=50)  # Non-unique identifier from XML
    lexical_entry = models.ForeignKey(LexicalEntry, on_delete=models.CASCADE, related_name="senses")

class Definition(models.Model):
    sense = models.ForeignKey(Sense, on_delete=models.CASCADE, related_name="definitions")
    text = models.TextField()

class Context(models.Model):
    sense = models.ForeignKey(Sense, on_delete=models.CASCADE, related_name="contexts")
    text = models.TextField()

class SyntacticBehaviour(models.Model):
    lexical_entry = models.ForeignKey(LexicalEntry, on_delete=models.CASCADE, related_name="syntactic_behaviours")
    subcategorization_frames = models.CharField(max_length=255, db_index=True)  # Added indexing for filtering
