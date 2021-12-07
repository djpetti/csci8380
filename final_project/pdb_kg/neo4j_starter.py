import asyncio
from downloader.graph_db import delete_all, form_kg, save_kg_to_json


def main():
    delete_all()
    asyncio.run(form_kg())
    save_kg_to_json("all")


if __name__ == '__main__':
    main()
