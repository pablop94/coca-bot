import datetime


def register_send_reminder_daily(job_queue, day, hour, minute):
    from meals.handlers import send_reminder

    job_queue.run_daily(
        send_reminder,
        time=datetime.time(hour=hour, minute=minute),
        days=(day,),
    )
