import argparse
import yaml

from . import crawler, scheduler


def load_config(path: str = "config.yaml") -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def main() -> None:
    parser = argparse.ArgumentParser(description="Baijiahao spider")
    sub = parser.add_subparsers(dest="cmd")

    run_p = sub.add_parser("run", help="run once")
    run_p.add_argument("--authors-file", default="data/authors.txt")
    run_p.add_argument("--limit-per-author", type=int)
    run_p.add_argument("--one")

    sched_p = sub.add_parser("schedule", help="run with scheduler")
    sched_p.add_argument("--cron", default="*/30 * * * *")
    sched_p.add_argument("--authors-file", default="data/authors.txt")

    args = parser.parse_args()
    cfg = load_config()
    if args.cmd == "run":
        if args.limit_per_author is not None:
            cfg.setdefault("throttle", {})["per_author_limit"] = args.limit_per_author
        if args.one:
            store = crawler.storage.Storage(
                save_json=cfg.get("storage", {}).get("save_json", True),
                save_text=cfg.get("storage", {}).get("save_text", True),
                sqlite=cfg.get("storage", {}).get("sqlite", True),
            )
            arts = crawler.crawl_author(args.one, cfg, store)
            crawler.storage.save_articles(arts, store)
            store.close()
        else:
            crawler.crawl_from_file(args.authors_file, cfg)
    elif args.cmd == "schedule":
        scheduler.start(args.cron, args.authors_file, cfg)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
