from configuration.environment import scheduler
from utils.birthday import check_birthdays


def setup_scheduler_jobs():
    scheduler.add_job(
        check_birthdays,
        trigger="cron",
        hour=22,
        minute=35,
        id="daily_birthdays",
        replace_existing=True
    )