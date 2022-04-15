import logging
from meals.decorators import developer_chat_id_required
from telegram import Update
from telegram.ext import CallbackContext

logger = logging.getLogger(__name__)


@developer_chat_id_required
def get_jobs_handler(update: Update, context: CallbackContext):

    jobs = []
    for job in context.job_queue.jobs():
        jobs.append(job.name.replace("_", "\\_"))

    update.message.reply_text(f"Los jobs son: {', '.join(jobs)}\\.")


@developer_chat_id_required
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
    repeated_jobs = sorted(repeated_jobs)
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
