# agentz/cli.py

import argparse
from agentz.commands import pull_kev

def main():
    parser = argparse.ArgumentParser(description="Agentz CLI")
    subparsers = parser.add_subparsers(dest="command")

    # Subcommand: pull kev
    pull_parser = subparsers.add_parser("pull", help="Pull CVEs from a feed")
    pull_parser.add_argument("feed", choices=["kev"], help="Which feed to pull")

    args = parser.parse_args()

    if args.command == "pull" and args.feed == "kev":
        pull_kev()

if __name__ == "__main__":
    main()
