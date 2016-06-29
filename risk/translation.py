from modeltranslation.translator import translator, TranslationOptions
from .models import ControlDomain, ControlProcess, ControlPractice, ControlActivity


class ControlDomainTranslationOptions(TranslationOptions):
    fields = ('domain', )


class ControlProcessTranslationOptions(TranslationOptions):
    fields = ('process_name', 'process_description', 'process_purpose')


class ControlPracticeTranslationOptions(TranslationOptions):
    fields = ('practice_name', 'practice_governance')


class ControlActivityTranslationOptions(TranslationOptions):
    fields = ('activity', 'activity_help')


translator.register(ControlDomain, ControlDomainTranslationOptions)
translator.register(ControlProcess, ControlProcessTranslationOptions)
translator.register(ControlPractice, ControlPracticeTranslationOptions)
translator.register(ControlActivity, ControlActivityTranslationOptions)
