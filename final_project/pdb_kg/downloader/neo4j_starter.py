import asyncio
from downloader import graph_db


def main():
    delete_all()
    asyncio.run(form_kg()）
    save_kg_to_json("all")


if __name__ == '__main__':
    main()
