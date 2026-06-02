"""
This module contains various configuration settings via
waffle switches for the completion app.
"""


from edx_toggles.toggles import WaffleSwitch

# The switch and namespace names variables are preserved for backward compatibility
WAFFLE_NAMESPACE = "completion"
ENABLE_COMPLETION_TRACKING = "enable_completion_tracking"  # pylint: disable=annotation-missing-token
# .. toggle_name: completion.enable_completion_tracking
# .. toggle_implementation: WaffleSwitch
# .. toggle_default: False
# .. toggle_description: Indicates whether or not to track completion of individual blocks. Keeping this disabled
#   will prevent creation of BlockCompletion objects in the database, as well as preventing completion-related
#   network access by certain xblocks.
# .. toggle_use_cases: open_edx
ENABLE_COMPLETION_TRACKING_SWITCH = WaffleSwitch(
    f"{WAFFLE_NAMESPACE}.{ENABLE_COMPLETION_TRACKING}",
    module_name=__name__,
)
# .. toggle_name: completion.enable_async_completion
# .. toggle_implementation: WaffleSwitch
# .. toggle_default: False
# .. toggle_description: Determines whether block completion updates are processed asynchronously via Celery.
#   When enabled, it mitigates database lock contention by offloading the insertion of BlockCompletion records
#   to a background worker, avoiding synchronous database waits during high-concurrency events. If disabled,
#   completions are processed synchronously within the main thread.
# .. toggle_use_cases: open_edx
ENABLE_ASYNC_COMPLETION_SWITCH = WaffleSwitch(
    f"{WAFFLE_NAMESPACE}.enable_async_completion",
    module_name=__name__,
)
