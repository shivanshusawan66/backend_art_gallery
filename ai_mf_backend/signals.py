from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from contextlib import contextmanager
from .models import Allowed_Response, Question, Section

# Delay the import of tasks
disable_signals = False

@contextmanager
def signals_disabled():
    global disable_signals
    disable_signals = True
    try:
        yield
    finally:
        disable_signals = False

# Update signal handlers to check the flag
@receiver(post_save, sender=Allowed_Response)
@receiver(post_delete, sender=Allowed_Response)
def handle_option_update(sender, instance, **kwargs):
    if disable_signals:
        return
    from .celery_tasks import calculate_option_scores, calculate_question_score
    calculate_option_scores.delay(instance.question.id)
    calculate_question_score.delay(instance.question.id)

@receiver(post_save, sender=Question)
@receiver(post_delete, sender=Question)
def handle_question_update(sender, instance, **kwargs):
    if disable_signals:
        return
    from .celery_tasks import calculate_section_score
    calculate_section_score.delay(instance.section.id)

@receiver(post_save, sender=Section)
@receiver(post_delete, sender=Section)
def handle_section_update(sender, instance, **kwargs):
    if disable_signals:
        return
    from .celery_tasks import calculate_section_score
    calculate_section_score.delay(instance.id)