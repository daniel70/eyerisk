from modeltranslation.translator import translator, TranslationOptions
from .models import Control


class ControlTranslationOptions(TranslationOptions):
    fields = ('domain', 'process_name', 'process_description', 'process_purpose', 'practice_name',
              'practice_governance', 'activity', 'activity_help')

translator.register(Control, ControlTranslationOptions)