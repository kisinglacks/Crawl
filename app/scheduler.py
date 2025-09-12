from apscheduler.schedulers.blocking import BlockingScheduler

from .crawler import crawl_from_file


def start(cron: str, authors_file: str, cfg: dict) -> None:
    sched = BlockingScheduler()
    sched.add_job(lambda: crawl_from_file(authors_file, cfg), "cron", **_parse_cron(cron))
    sched.start()


def _parse_cron(cron: str) -> dict:
    fields = cron.split()
    keys = ["minute", "hour", "day", "month", "day_of_week"]
    return {k: v for k, v in zip(keys, fields)}
