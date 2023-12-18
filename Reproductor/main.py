import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QLabel, QPushButton, QStatusBar, QTabWidget,
                             QWidget, QHBoxLayout, QVBoxLayout, QDockWidget, QListWidget, QFileDialog,
                             QListWidgetItem)

from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtCore import QUrl

from PyQt6.QtGui import QPixmap, QAction, QKeySequence, QIcon
from PyQt6.QtCore import Qt, QStandardPaths

class MainWindow(QMainWindow):
    
    def __init__(self):
        super().__init__()
        self.initialize_ui()
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.current_music_folder = ""
        with open('Reproductor/estilos.css','r') as file:
            style = file.read()
        self.setStyleSheet(style)
        self.player = None
        self.playing_reproductor = False
        
    def initialize_ui(self):
        self.setGeometry(100, 100, 800, 800)
        self.setWindowTitle("Reproductor de música")
        self.generate_main_window()
        self.create_dock()
        self.create_action()
        self.create_menu()
        self.show()
        
    def generate_main_window(self):
        tab_bar = QTabWidget(self)
        self.reproductor_container = QWidget()
        self.settings_container = QWidget()
        tab_bar.addTab(self.reproductor_container, "Reproductor")
        tab_bar.addTab(self.settings_container, "Settings")
        
        self.generate_reproductor_tab()
        self.generate_settings_tab()
        
        tab_h_box = QHBoxLayout()
        tab_h_box.addWidget(tab_bar)
        
        main_container = QWidget()
        main_container.setLayout(tab_h_box)
        self.setCentralWidget(main_container)
        
    def generate_reproductor_tab(self):
        main_v_box = QVBoxLayout()
        buttons_h_box = QHBoxLayout()
        
        song_image = QLabel()
        pixmap = QPixmap("Reproductor/recursos/imagenes/iconoMusica01.png").scaled(500,500)  
        song_image.setPixmap(pixmap)
        song_image.setScaledContents(True)
        
        button_repeat = QPushButton()
        button_repeat.setObjectName('button_repeat')
        button_before = QPushButton()
        button_before.setObjectName('button_before')
        self.button_play = QPushButton()
        button_before.clicked.connect(self.play_previous_song)
        self.button_play.setObjectName('button_play')
        self.button_play.clicked.connect(self.play_pause_song)
        button_next = QPushButton()
        button_next.setObjectName('button_next')
        button_random = QPushButton()
        button_next.clicked.connect(self.play_next_song)
        button_random.setObjectName('button_random')
        button_repeat.setFixedSize(40,40)
        button_before.setFixedSize(40,40)
        self.button_play.setFixedSize(50,50)
        button_next.setFixedSize(40,40)
        button_random.setFixedSize(40,40)
        buttons_h_box.addWidget(button_repeat)
        buttons_h_box.addWidget(button_before)
        buttons_h_box.addWidget(self.button_play)
        buttons_h_box.addWidget(button_next)
        buttons_h_box.addWidget(button_random)
        buttons_container = QWidget()
        buttons_container.setLayout(buttons_h_box)
        
        main_v_box.addWidget(song_image)
        main_v_box.addWidget(buttons_container)
        
        self.reproductor_container.setLayout(main_v_box)
        
    def generate_settings_tab(self):
        pass  
    
    def create_action(self):
        self.listar_musica_action = QAction('Listar musica', self, checkable=True)
        self.listar_musica_action.setShortcut(QKeySequence("Ctrl+L"))
        self.listar_musica_action.setStatusTip("Aqui puede listar o no la música a reproducir")
        self.listar_musica_action.triggered.connect(self.list_music)
        self.listar_musica_action.setChecked(True)
        
        self.open_folder_music_action = QAction('Abrir Carpeta', self)
        self.open_folder_music_action.setShortcut(QKeySequence("Ctrl+O"))
        self.open_folder_music_action.setStatusTip("Abre tu carpeta de música")
        self.open_folder_music_action.triggered.connect(self.open_folder_music)
    
    def create_menu(self):
        self.menuBar()
        
        menu_file = self.menuBar().addMenu("File")
        menu_file.addAction(self.open_folder_music_action)
        
        menu_view = self.menuBar().addMenu("View")
        menu_view.addAction(self.listar_musica_action)
        
    def create_dock(self):
        self.songs_list = QListWidget()
        self.dock = QDockWidget()
        self.dock.setWindowTitle("Lista de canciones")
        self.dock.setAllowedAreas(
            Qt.DockWidgetArea.LeftDockWidgetArea | 
            Qt.DockWidgetArea.RightDockWidgetArea
        )
        self.songs_list.itemSelectionChanged.connect(self.handle_song_selection)
        self.dock.setWidget(self.songs_list)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.dock)
    
    def list_music(self):
        if self.listar_musica_action.isChecked():
            self.dock.show()
        else:
            self.dock.hide()
            
    def open_folder_music(self):
        initial_dir = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.MusicLocation)
        self.current_music_folder = QFileDialog.getExistingDirectory(None, "Seleccione una carpeta", initial_dir)
        icon = QIcon("Reproductor/recursos/imagenes/iconoPlay.png")
        for archivo in os.listdir( self.current_music_folder):
            ruta_archivo = os.path.join( self.current_music_folder, archivo)
            if ruta_archivo.endswith(".mp3"):
                item = QListWidgetItem(archivo)
                item.setIcon(icon)
                self.songs_list.addItem(item)
                
    def create_player(self):
        if self.player:
            self.player.deleteLater()
        self.player = QMediaPlayer()
        self.audioOutpot = QAudioOutput()
        self.player.setAudioOutput(self.audioOutpot)
        self.player.mediaStatusChanged.connect(self.media_status_changed)
        self.audioOutpot.setVolume(1.0)
        
        
    def play_pause_song(self):
        if self.player is not None:
            if self.playing_reproductor:
                self.button_play.setStyleSheet("image: url(Reproductor/recursos/imagenes/botonPausa.png);")
                self.player.pause()
                self.playing_reproductor = False
            else:
                self.button_play.setStyleSheet("image: url(Reproductor/recursos/imagenes/iconoPlay.png);")
                self.player.play()
                self.playing_reproductor = True
        else:
            print("No se ha cargado ninguna canción. Seleccione una canción antes de reproducir.")

    def play_previous_song(self):
        if self.songs_list.count() > 0:
            current_row = self.songs_list.currentRow()
            previous_row = (current_row - 1) % self.songs_list.count()
            self.songs_list.setCurrentRow(previous_row)
            self.handle_song_selection()
    
    def play_next_song(self):
        if self.songs_list.count() > 0:
            current_row = self.songs_list.currentRow()
            next_row = (current_row + 1) % self.songs_list.count()
            self.songs_list.setCurrentRow(next_row)
            self.handle_song_selection()
        
    def media_status_changed(self, status):
        print('status', status)
        if status == QMediaPlayer.MediaStatus.LoadedMedia:
            self.player.play()
                
    def handle_song_selection(self):
        selected_item = self.songs_list.currentItem()
        if selected_item:
            song_name = selected_item.data(0)
            song_folder_path = os.path.join( self.current_music_folder, song_name)
            self.create_player()
            source = QUrl.fromLocalFile(song_folder_path)
            self.player.setSource(source)
            self.playing_reproductor = True
        
        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec())
