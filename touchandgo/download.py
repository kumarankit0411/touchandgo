from os.path import join
from time import sleep
from datetime import datetime

from libtorrent import add_magnet_uri, session


TMP_DIR = "/tmp"


class DownloadManager(object):
    def __init__(self, magnet, callback=None):
        self.start_time = datetime.now()
        self.session = session()
        self.piece_strat = 5
        self.first_pieces = True
        self.callback = callback

        params = {"save_path": TMP_DIR,
                  "allocation": "compact"}
        self.handle = add_magnet_uri(self.session, magnet, params)

        while not self.handle.has_metadata():
            sleep(.1)
        self.session.listen_on(6881, 6891)
        self.session.start_dht()

        chunks_strat = self.initial_strategy()

        for i in range(self.piece_strat):
            self.handle.piece_priority(i, 7)
            self.handle.set_piece_deadline(i, 10000)

        while True:
            if not self.handle.is_seed():
                self.strategy_master(chunks_strat)
            self.defrag()
            sleep(1)

    def get_biggest_file(self):
        info = self.handle.get_torrent_info()
        biggest_file = ("", 0)
        files = info.files()
        for file_ in files:
            if file_.size > biggest_file[1]:
                biggest_file = [file_.path, file_.size]

        return biggest_file

    def strategy_master(self, chunks_strat):
        status = self.handle.status()
        pieces = status.pieces
        primera = pieces[:self.piece_strat]

        if all(primera):
            self.handle.set_sequential_download(False)
            pieces_strat = pieces[self.piece_strat:self.piece_strat + chunks_strat]
            if self.first_pieces or all(pieces_strat):
                if not self.first_pieces:
                    self.piece_strat += chunks_strat
                else:
                    if self.callback is not None:
                        self.callback(self)

                for i in range(self.piece_strat, self.piece_strat + chunks_strat):
                    self.handle.piece_priority(i, 7)
                    self.handle.set_piece_deadline(i, 10000)

                for i in range(self.piece_strat+chunks_strat,
                               self.piece_strat + chunks_strat*2):
                    self.handle.piece_priority(i, 5)
                    self.handle.set_piece_deadline(i, 20000)
                self.first_pieces = False

    def defrag(self):
        status = self.handle.status()
        numerales = "\n" * 50
        for i, piece in enumerate(status.pieces):
            numeral = "#" if piece else " "
            numeral += str(self.handle.piece_priority(i))
            numerales += numeral
        print numerales

        state_str = ['queued', 'checking', 'downloading metadata', 'downloading', 'finished', 'seeding', 'allocating']
        print '%.2f%% complete (down: %.1f kb/s up: %.1f kB/s peers: %d) %s' % \
                (status.progress * 100, status.download_rate / 1000, status.upload_rate / 1000, \
                    status.num_peers, state_str[status.state])
        print datetime.now() - self.start_time

    def initial_strategy(self):
        self.handle.set_sequential_download(True)
        status = self.handle.status()
        return len(status.pieces) / 25


from flask import Flask, Response

def get_file(filename):
    try:
        src = join(TMP_DIR, filename[0])
        return open(src).read()
    except IOError as exc:
        return str(exc)

def callback(manager):
    app = Flask(__name__)
    app.config.from_object(__name__)

    @app.route('/', methods=['GET'])
    def serve_file():
        print "hola"
        content = get_file(manager.get_biggest_file())
        return Response(content)
    app.run()



magnet = "magnet:?xt=urn:btih:d9bdf203693c508cbff515602ea4898ae2ffa4a6&dn=Suits+S04E08+HDTV+x264-KILLERS%5Bettv%5D&tr=udp%3A//tracker.openbittorrent.com%3A80&tr=udp%3A//tracker.publicbt.com%3A80&tr=udp%3A//tracker.istole.it%3A6969&tr=udp%3A//open.demonii.com%3A1337"
DownloadManager(magnet, callback)