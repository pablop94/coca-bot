from unittest.mock import MagicMock, call
from django.test import TestCase, override_settings

from meals.handlers.commands_admin import (
    get_jobs_handler,
    cleanup_jobs_handler,
)
from meals.tests.base import get_mock_context, get_mock_update


class AdminCommandsTest(TestCase):
    @override_settings(DEVELOPER_CHAT_ID=1)
    def test_get_jobs_handler(self, *args):
        context = get_mock_context()
        update = get_mock_update()
        job1 = MagicMock()
        job1.name = "jobcito"
        job2 = MagicMock()
        job2.name = "jobcito2"
        context.job_queue = MagicMock()
        context.job_queue.jobs = MagicMock(return_value=[job1, job2])
        get_jobs_handler(update, context)

        update.message.reply_text.assert_called_once_with(
            "Los jobs son: jobcito, jobcito2\\."
        )

    @override_settings(DEVELOPER_CHAT_ID=1)
    def test_cleanup_jobs_handler_no_repeated_jobs(self, *args):
        context = get_mock_context()
        update = get_mock_update()
        job1 = MagicMock()
        job1.name = "ajob"
        job2 = MagicMock()
        job2.name = "bjob"
        context.job_queue = MagicMock()
        context.job_queue.jobs = MagicMock(return_value=[job1, job2])
        cleanup_jobs_handler(update, context)

        update.message.reply_text.assert_called_once_with(
            "- Los jobs son: ajob, bjob.\n\nNo hay jobs repetidos.",
            parse_mode=None,
        )

    @override_settings(DEVELOPER_CHAT_ID=1)
    def test_cleanup_jobs_handler_repeated_jobs(self, *args):
        context = get_mock_context()
        update = get_mock_update()
        job1 = MagicMock()
        job1.name = "jobcito"
        job2 = MagicMock()
        job2.name = "jobcito"
        context.job_queue = MagicMock()
        context.job_queue.jobs = MagicMock(return_value=[job1, job2])
        cleanup_jobs_handler(update, context)

        update.message.reply_text.assert_has_calls(
            [
                call(
                    "- Los jobs son: jobcito.\n\n- Jobs repetidos: jobcito",
                    parse_mode=None,
                ),
                call(
                    "Los jobs repetidos se marcaron para borrar.",
                    parse_mode=None,
                ),
            ]
        )

        job2.schedule_removal.assert_called_once()
