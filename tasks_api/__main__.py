import argparse
from .server import create_server


def main():
    p = argparse.ArgumentParser(description="Run the tasks API.")
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--port", type=int, default=8000)
    p.add_argument("--db", default="tasks.db", help="SQLite file path")
    args = p.parse_args()
    server = create_server(args.host, args.port, args.db)
    print(f"Listening on http://{args.host}:{args.port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
