import logging
from meals.decorators import chat_id_required
from telegram import Update
from telegram.ext import CallbackContext

logger = logging.getLogger(__name__)


@chat_id_required(allow_admin_run=True, allow_user_run=False)
def get_jobs_handler(update: Update, context: CallbackContext):

    jobs = []
    for job in context.job_queue.jobs():
        jobs.append(job.name.replace("_", "\\_"))

    update.message.reply_text(f"Los jobs son: {', '.join(jobs)}\\.")


@chat_id_required(allow_admin_run=True, allow_user_run=False)
def cleanup_jobs_handler(update: Update, context: CallbackContext):
    cleanup_jobs(update, context.job_queue.jobs())


def cleanup_jobs(update: Update, jobs):
    logger.info("Starting jobs cleanup")

    current_jobs = set()
    repeated_jobs = set()

    for job in jobs:
        if job.name in current_jobs:
            repeated_jobs.add(job.name)
            job.schedule_removal()
        current_jobs.add(job.name)
    current_jobs = sorted(current_jobs)
    message = f"- Los jobs son: {', '.join(current_jobs)}.\n\n" + (
        f"- Jobs repetidos: {', '.join(repeated_jobs)}"
        if repeated_jobs
        else "No hay jobs repetidos."
    )
    update.message.reply_text(message, parse_mode=None)
    if repeated_jobs:
        update.message.reply_text(
            "Los jobs repetidos se marcaron para borrar.",
            parse_mode=None,
        )


COMMANDS_ARGS = [
    ("jobs", get_jobs_handler),
    ("cleanup", cleanup_jobs_handler),
]
