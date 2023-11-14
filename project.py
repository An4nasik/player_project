import sys
import pygame
from PyQt5.QtWidgets import QMainWindow, QPushButton, QProgressBar, QLabel, QTableView, QFileDialog, QApplication
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QPixmap
from PyQt5.QtSql import QSqlDatabase, QSqlTableModel
import librosa
import os
from mutagen import File
import sqlite3

class Form(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setGeometry(100, 100, 600, 600)
        self.filechoose = QPushButton("выбрать файл", self)
        self.filechoose.move(10, 10)
        self.filechoose.clicked.connect(self.add_song)
        self.filechoose.resize(150, 30)
        self.player = pygame.mixer
        self.player.init()
        self.song_starter = QPushButton("Начать воспроизведение", self)
        self.song_starter.setEnabled(False)
        self.song_starter.resize(150, 30)
        self.song_starter.move(10, 40)
        self.song_starter.clicked.connect(self.run)
        self.playlist_starter = QPushButton("Запустить плейлист", self)
        self.playlist_starter.setEnabled(False)
        self.playlist_starter.resize(150, 30)
        self.playlist_starter.move(10, 100)
        self.playlist_starter.clicked.connect(self.playlist_run)
        self.mulltifilechoose = QPushButton("Выбрать файлы для плейлиста", self)
        self.mulltifilechoose.clicked.connect(self.multi_add_song)
        self.mulltifilechoose.resize(150, 30)
        self.mulltifilechoose.move(10, 70)
        self.pause_button = QPushButton("Пауза", self)
        self.pause_button.move(10, 130)
        self.pause_button.clicked.connect(self.pause)
        self.unpause_button = QPushButton("UnПауза", self)
        self.unpause_button.move(10, 160)
        self.unpause_button.resize(150, 30)
        self.unpause_button.clicked.connect(self.unpause)
        self.unpause_button.setEnabled(False)
        self.pause_button.setEnabled(False)
        self.pause_button.resize(150, 30)
        self.plus_button = QPushButton("Увеличить громкость", self)
        self.plus_button.move(10, 190)
        self.plus_button.resize(150, 30)
        self.plus_button.clicked.connect(self.plus_volume)
        self.minus_button = QPushButton("Уменьшить громкость", self)
        self.minus_button.move(10, 220)
        self.minus_button.resize(150, 30)
        self.minus_button.clicked.connect(self.minus_volume)
        self.progressBar = QProgressBar(self)
        self.progressBar.move(300, 300)
        self.progressBar.resize(300, 25)
        self.progressBar.hide()
        self.player.music.set_volume(0.1)
        self.work_files = []
        self.forward_button = QPushButton("->", self)
        self.forward_button.resize(75, 30)
        self.forward_button.move(85, 250)
        self.forward_button.setEnabled(False)
        self.forward_button.clicked.connect(self.forward)
        self.back_button = QPushButton("<-", self)
        self.back_button.move(10, 250)
        self.back_button.resize(75, 30)
        self.back_button.setEnabled(False)
        self.back_button.clicked.connect(self.backward)
        self.cover_lable = QLabel(self)
        self.cover_lable.resize(300, 300)
        self.cover_lable.move(300, 0)
        self.clear_button = QPushButton("Отчистить историю", self)
        self.clear_button.clicked.connect(self.cleanig)
        self.clear_button.move(10, 280)
        self.clear_button.resize(150, 30)

        db = QSqlDatabase.addDatabase('QSQLITE')
        db.setDatabaseName('songs.sqlite')
        db.open()
        self.view = QTableView(self)
        self.model = QSqlTableModel(self, db)
        self.model.setTable('user_songs')
        self.model.select()
        self.view.setModel(self.model)
        self.view.move(10, 330)
        self.view.resize(220, 150)


    def cleanig(self):
        try:
            con = sqlite3.connect("songs.sqlite")
            cur = con.cursor()
            cur.execute(f"""Delete from user_songs""")
            con.commit()
            cur.close()
        except Exception:
            pass
        self.model.select()
        self.view.setModel(self.model)

    def timerEvent(self, *args, **kwargs):
        #работа progressbar-а
        if self.step <= 100:
            self.progressBar.setValue(self.step)
            self.step = self.step + 1
        else:
            self.time.stop()
            self.progressBar.setValue(0)
            self.cover_lable.hide()

        if len(self.work_files) != 0 and not self.player.music.get_busy():
            self.playlist_continue_run()

    def playlist_continue_run(self):
        #воспроизведение плейлистов
        self.player.music.unload()
        self.player.music.load(self.work_files[0])
        self.player.music.play()
        self.add_cover(self.work_files.pop(0))

    def user_songs_add(self):
        #работа с таблицей sql

            for path in self.work_files:
                try:
                    n = str(path.split(sep="/")[-1])
                    d = str(int(librosa.get_duration(path=path)))
                    con = sqlite3.connect("songs.sqlite")
                    cur = con.cursor()
                    cur.execute(f"""INSERT INTO user_songs
                    ('название', 'длительность')
                    VALUES
                    ('{n}', "{d}")""")
                    con.commit()
                    cur.close()
                except Exception:
                    break
            self.model.select()
            self.view.setModel(self.model)



    def add_cover(self, filepath):
        #обложка файла
        f = File(filepath)
        if 'APIC:' in f.keys():
            self.cover_lable.show()
            cover_data = f['APIC:'].data
            cover = "cover.png"
            with open(cover, 'wb') as file:
                file.write(cover_data)
                self.pixmap = QPixmap(cover)
                self.cover_lable.setPixmap(self.pixmap)
            os.remove(cover)

    def add_song(self):
        self.work_files = []
        #добавление файла
        self.file = QFileDialog.getOpenFileUrl(filter="Аудиофайлы(*.mp3)")[0].path()[1:]
        self.work_files = [self.file]
        self.song_starter.setEnabled(True)
        self.cover_lable.hide()
        self.add_cover(self.file)
        self.dur = int(librosa.get_duration(path=self.file) * 10)
        self.user_songs_add()
        self.back_button.setEnabled(True)
        self.forward_button.setEnabled(True)

    def multi_add_song(self):
        self.work_files = []
        #добавление файлов
        self.dur = 0
        self.files = QFileDialog.getOpenFileUrls(filter="Аудиофайлы(*.mp3)")[0]
        self.playlist_starter.setEnabled(True)
        for x in self.files:
            self.dur = self.dur + int(librosa.get_duration(path=x.path()[1:]) * 10)
            self.work_files.append(x.path()[1:])
        self.user_songs_add()
        self.back_button.setEnabled(True)
        self.forward_button.setEnabled(True)

    def run(self):
        #запуск одного файла
        self.player.music.unload()
        self.player.music.load(self.file)
        self.player.music.play(loops=0)
        self.pause_button.setEnabled(True)
        self.progressBar.show()
        self.progressBar.setValue(0)
        self.time = QTimer(self)
        self.time.timeout.connect(self.timerEvent)
        self.step = 0
        self.time.start(self.dur)

    def playlist_run(self):
        #запуск нескольких файлов
        self.cover_lable.hide()
        self.player.music.unload()
        work_files = []
        for x in self.files:
            work_files.append(x.path()[1:])
        self.player.music.load(work_files[0])
        self.player.music.play()
        self.add_cover(work_files.pop(0))
        self.work_files = work_files
        self.pause_button.setEnabled(True)
        self.progressBar.show()
        self.progressBar.setValue(0)
        self.time = QTimer(self)
        self.time.timeout.connect(self.timerEvent)
        self.step = 0
        self.time.start(self.dur)

    def pause(self):
        self.player.music.pause()
        self.pause_button.setEnabled(False)
        self.unpause_button.setEnabled(True)
        self.time.stop()

    def unpause(self):
        self.player.music.unpause()
        self.pause_button.setEnabled(True)
        self.unpause_button.setEnabled(False)
        self.time.start()

    def plus_volume(self):
        if self.player.music.get_volume() != 1:
            self.player.music.set_volume(self.player.music.get_volume() + 0.1)

    def minus_volume(self):
        if self.player.music.get_volume() != 0:
            self.player.music.set_volume(self.player.music.get_volume() - 0.1)

    def forward(self):
        if self.player.music.get_pos() // 1000 + 1 < self.dur // 10:
            print(self.player.music.get_pos())
            self.player.music.set_pos((self.player.music.get_pos() // 1000) + 1)
            self.step = self.step + 1000 // self.dur
            self.progressBar.setValue(self.step)

    def backward(self):
        if self.player.music.get_pos() // 1000 - 1 < self.dur // 10:
            self.player.music.set_pos((self.player.music.get_pos() // 1000) - 1)
            self.step = self.step - 1000 // self.dur
            self.progressBar.setValue(self.step)



if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Form()
    ex.setObjectName("MainWindow")
    ex.setStyleSheet("#MainWindow{border-image:url(icon.jpg)}")
    ex.show()
    sys.exit(app.exec_())
