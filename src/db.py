# built in
import sqlite3
import datetime

# 3rd party
import meshtastic.serial_interface
from pubsub import pub


def dict_factory(cursor, row):
    fields = [column[0] for column in cursor.description]
    return {key: value for key, value in zip(fields, row)}


class Database:
    def __init__(self, path):
        self.path = path
        self.connection = None
        self.cursor = None
    def __enter__(self):
        self.connection = sqlite3.connect(self.path)
        self.connection.row_factory = dict_factory
        self.cursor = self.connection.cursor()
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS messages (
                uuid INTEGER,
                sender TEXT,
                target TEXT,
                text TEXT,
                channel INTEGER,
                timestamp TEXT
            );
            """
        )
        return self
    def __exit__(self, exception_type, exception_value, exception_traceback):
        self.connection.commit()
        self.connection.close()
        self.connection = None
        self.cursor = None
    def insert(self, uuid, sender, target, text, channel, timestamp):
        if not self.connection:
            raise RuntimeError('No connection found, please use `with Database("/path") as db:` syntax')
        self.cursor.execute(
            "INSERT INTO messages VALUES (?, ?, ?, ?, ?, ?);",
            [uuid, sender, target, text, channel, timestamp]
        )
    def get(
        self,
        limit=None,
        dm=None
    ):
        if not self.connection:
            raise RuntimeError('No connection found, please use `with Database("/path") as db:` syntax')
        results = None
        if not limit and not dm:
            results = self.cursor.execute("SELECT * FROM messages ORDER BY timestamp DESC;")
        elif limit:
            results = self.cursor.execute("SELECT * FROM messages ORDER BY timestamp DESC LIMIT ?;", [limit])
        elif dm:
            results = self.cursor.execute("SELECT * FROM messages WHERE target=? ORDER BY timestamp DESC;", [dm])
        return [row for row in results]


def onMessage(packet, interface, db_path="db.sqlite"):
    uuid = packet['id']
    sender = packet['fromId']
    target = packet['toId']
    text = packet['decoded']['payload'].decode()
    channel = packet.get("channel", 0)
    timestamp = datetime.datetime.fromtimestamp(packet['rxTime'])
    timestamp = timestamp.isoformat()
    with Database(db_path) as db:
        db.insert(uuid, sender, target, text, channel, timestamp)


def start():
    """For use in the main app"""
    pub.subscribe(onMessage, "meshtastic.receive.text")

if __name__ == "__main__": # pragma: no cover
    interface = meshtastic.serial_interface.SerialInterface()
    while True:
        pub.subscribe(onMessage, "meshtastic.receive.text")
