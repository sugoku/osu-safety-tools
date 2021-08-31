import sys
import os
import json
from dbparse import parseOsuDb
from pathlib import Path
from zipfile import ZipFile
import tempfile
import shutil

from PyQt5.QtWidgets import QMainWindow, QDialog, QApplication, QFileDialog
from PyQt5.QtCore import QThreadPool, QRunnable, pyqtSignal, QThread
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5 import uic

from osubg import generate_bg
from osu_audio_gen import generate_audio

osu_directory = Path("C:\\Program Files (x86)\\osu!")
songs_folder = osu_directory/'Songs'

def db_parse(p):
    with open(p/"osu!.db", "rb") as db:
        data = parseOsuDb(db.read())
    beatmaps = sorted(data['beatmaps'].values(), key=lambda x: x['beatmap_id'])
    with open('db.json', 'w') as db_out:
        json.dump(beatmaps, db_out)
    return beatmaps
    
class AudioThread(QThread):
    progress = pyqtSignal(int)
    
    def __init__(self, parent=None):
        super(AudioThread, self).__init__(parent)
        self.osu_fn = None
    
    def run(self):
        generate_audio(self.osu_fn, self.progress)
    

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi("osu-tools.ui", self)

        self.setWindowTitle("sugoku's osu! safety tools")
        
        self.listModel = QStandardItemModel()
        self.listView.setModel(self.listModel)
        
        self.beatmap = None
        self.osu_fn = None
        self.audio_fn = None
        
        self.replace_image.clicked.connect(self.on_replace_image)
        self.replace_audio.clicked.connect(self.on_replace_audio)
        self.restore_audio.clicked.connect(self.on_restore_audio)
        
        self.lineEdit.textChanged.connect(self.update_listview)
        self.listView.clicked.connect(self.on_beatmap_select)
        
        self.action_refresh.triggered.connect(self.update_beatmaps)
        self.action_manual.triggered.connect(self.manual_beatmap_select)
        self.action_osz.triggered.connect(self.osz_beatmap_select)
        
        self.load_beatmaps()
        self.update_listview()
        
    def load_beatmaps(self):
        try:
            with open('db.json') as db_in:
                self.beatmaps = json.load(db_in)
                self.beatmaplist = [f"{i}: {x['folder_name']} - {x['version']}" for i, x in enumerate(self.beatmaps)]
        except:
            self.update_beatmaps()
        
    def update_beatmaps(self):
        self.beatmaps = db_parse(osu_directory)
        self.beatmaplist = [f"{i}: {x['folder_name']} - {x['version']}" for i, x in enumerate(self.beatmaps)]
        
    def update_listview(self):
        self.listModel.clear()
        for beatmap in self.beatmaplist:
            if not len(self.lineEdit.text()) or self.lineEdit.text().lower() in beatmap.lower():
                self.listModel.appendRow(QStandardItem(beatmap))
                
    def manual_beatmap_select(self):
        self.osu_fn = Path(QFileDialog.getOpenFileName(parent=self, caption='Open file', directory=str(osu_directory), filter='*.osu')[0])
        self.audio_fn = None
        self.folder.setText(f"Folder: {self.osu_fn.parent}")
        self.on_replace_audio()
        
    def osz_beatmap_select(self):
        self.osz_fn = Path(QFileDialog.getOpenFileName(parent=self, caption='Open file', directory=str(osu_directory), filter='*.osz')[0])
        dirname = tempfile.mkdtemp()
        self.dp = Path(dirname)
        with ZipFile(self.osz_fn) as z:
            z.extractall(path=self.dp)
        l = list(self.dp.glob('*.osu'))
        if not len(l):
            self.folder.setText(f"Error: no .osu files found in {self.osz_fn}")
        self.osu_fn = l[0]
        self.audio_fn = None
        self.folder.setText(f"Folder: {self.osu_fn.parent}")
        self.on_replace_osz()
            
    def on_beatmap_select(self):
        self.beatmap = self.beatmaps[int(str(self.listView.currentIndex().data()).split(':')[0])]
        song_folder = songs_folder/(self.beatmap['folder_name'])
        self.osu_fn = song_folder/(self.beatmap['osu_file'])
        self.audio_fn = song_folder/(self.beatmap['audio_file'])
        
        self.folder.setText(f"Folder: {song_folder}")
        if Path(str(self.audio_fn)+".bak").exists():
            self.status.setText("Status: A backup audio file exists for the map! It will be replaced if you generate a new one.")
        else:
            self.status.setText("Status: The audio file has not been replaced yet (no backup found).")
            
    def on_replace_image(self):
        generate_bg(self.osu_fn)
        self.status.setText("Status: Image replaced succesfully!")
    
    def on_replace_audio(self):
        self.thread = AudioThread()
        self.thread.osu_fn = self.osu_fn
        self.thread.finished.connect(self.success_replace_audio)
        self.thread.progress.connect(self.update_progress_bar)
        self.thread.start()
        
    def on_replace_osz(self):
        self.thread = AudioThread()
        self.thread.osu_fn = self.osu_fn
        self.thread.finished.connect(self.success_replace_osz)
        self.thread.progress.connect(self.update_progress_bar)
        self.thread.start()
        
    def update_progress_bar(self, i):
        self.progressBar.setValue(i)
        
    def success_replace_audio(self):
        self.status.setText("Status: Audio replaced succesfully!")
        
    def success_replace_osz(self):
        os.remove(self.osz_fn)
        shutil.make_archive(self.osz_fn, 'zip', self.dp)
        os.rename(self.osz_fn.with_suffix(self.osz_fn.suffix + '.zip'), self.osz_fn)
        shutil.rmtree(self.dp)
        
        self.status.setText("Status: osz audio replaced succesfully!")
    
    def on_restore_audio(self):
        bak_fn = Path(str(self.audio_fn)+".bak")
        # print(bak_fn)
        self.status.setText("Status: Backup restored succesfully!")
        
        if bak_fn.exists():
            os.remove(self.audio_fn)
            os.rename(bak_fn, self.audio_fn)
        else:
            self.status.setText("Status: You cannot restore a backup that doesn't exist!")
                
                
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec_()