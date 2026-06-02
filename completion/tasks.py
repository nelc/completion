"""
Celery tasks for completion tracking.
"""
import logging

from django.contrib import auth

from celery import shared_task
from opaque_keys import InvalidKeyError
from opaque_keys.edx.keys import LearningContextKey, UsageKey
from xblock.completable import XBlockCompletionMode
from xblock.core import XBlock

from .models import BlockCompletion

log = logging.getLogger(__name__)
User = auth.get_user_model()


@shared_task(bind=True, max_retries=3)
def submit_block_completion_task(self, user_id, usage_id, course_id, score_deleted=False, grader_response=False):
    """
    Async task to handle block completion submissions, reducing database lock contention.
    """
    try:
        block_key = UsageKey.from_string(usage_id)
    except InvalidKeyError:
        log.exception("Unable to parse XBlock usage_id for completion: %s", usage_id)
        return

    if block_key.context_key.is_course and block_key.context_key.run is None:
        # In the case of old mongo courses, the context_key cannot be derived
        # from the block key alone since it will be missing run info:
        course_key_with_run = LearningContextKey.from_string(course_id)
        block_key = block_key.replace(course_key=course_key_with_run)

    block_cls = XBlock.load_class(block_key.block_type)
    if XBlockCompletionMode.get_mode(block_cls) != XBlockCompletionMode.COMPLETABLE:
        return

    if getattr(block_cls, 'has_custom_completion', False):
        return

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        log.exception("User %s not found for async completion.", user_id)
        return

    completion = 0.0 if score_deleted else 1.0

    if not grader_response:
        BlockCompletion.objects.submit_completion(
            user=user,
            block_key=block_key,
            completion=completion,
        )
