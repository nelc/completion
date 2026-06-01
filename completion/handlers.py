"""
Signal handlers to trigger completion updates.
"""

import logging

from django.contrib import auth

from . import waffle
from .tasks import submit_block_completion_async

log = logging.getLogger(__name__)
User = auth.get_user_model()


def scorable_block_completion(sender, **kwargs):  # pylint: disable=unused-argument
    """
    When a problem is scored, submit a new BlockCompletion for that block.
    """
    if not waffle.ENABLE_COMPLETION_TRACKING_SWITCH.is_enabled():
        return

    usage_id = kwargs.get('usage_id')
    user_id = kwargs.get('user_id')
    course_id = kwargs.get('course_id')
    score_deleted = kwargs.get('score_deleted', False)
    grader_response = kwargs.get('grader_response', False)

    if not all([usage_id, user_id, course_id]):
        log.warning("Missing required kwargs for scorable_block_completion.")
        return

    task_kwargs = {
        'user_id': user_id,
        'usage_id': usage_id,
        'course_id': course_id,
        'score_deleted': score_deleted,
        'grader_response': grader_response
    }

    if waffle.ENABLE_ASYNC_COMPLETION_SWITCH.is_enabled():
        submit_block_completion_async.apply_async(kwargs=task_kwargs)
    else:
        submit_block_completion_async.apply(kwargs=task_kwargs)
