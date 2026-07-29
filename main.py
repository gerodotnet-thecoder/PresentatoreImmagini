import sys
import os
import tempfile
import urllib.request
import base64
import re
import math
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QListWidget, QListWidgetItem, QDialog, QTextBrowser
from PyQt6.QtCore import Qt, pyqtSignal, QUrl, QByteArray, QEvent
from PyQt6.QtGui import QPainter, QColor, QPixmap, QImage, QPolygon, QIcon
from PyQt6.QtCore import QPoint
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtMultimediaWidgets import QVideoWidget

__version__ = "v2.2"

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

valid_image_exts = ('.png', '.jpg', '.jpeg', '.bmp', '.webp', '.gif')
valid_video_exts = ('.mp4', '.avi', '.mkv', '.mov', '.wmv', '.m4v')

def is_video(path):
    return path.lower().endswith(valid_video_exts)

def create_video_thumbnail():
    pixmap = QPixmap(50, 50)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    
    # Sfondo
    painter.setBrush(QColor(40, 40, 40, 220))
    painter.setPen(QColor(100, 100, 100))
    painter.drawRoundedRect(0, 0, 49, 49, 8, 8)
    
    # Simbolo Play rosso
    painter.setBrush(QColor(244, 67, 54))
    painter.setPen(Qt.PenStyle.NoPen)
    
    triangle = QPolygon([
        QPoint(18, 15),
        QPoint(18, 35),
        QPoint(35, 25)
    ])
    painter.drawPolygon(triangle)
    painter.end()
    return pixmap

class ClickableLabel(QLabel):
    clicked = pyqtSignal()
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()

class ChangelogDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Changelog")
        self.resize(400, 300)
        self.setStyleSheet("background-color: #222; color: #fff;")
        
        layout = QVBoxLayout()
        self.text_browser = QTextBrowser()
        self.text_browser.setStyleSheet("background-color: #333; color: white; border: none; font-family: sans-serif; font-size: 13px; padding: 10px;")
        
        html_content = """
        <h2 style='color: #4CAF50;'>Changelog delle versioni</h2>
        
        <h3 style='color: #81c784;'>Versione 2.2</h3>
        <ul>
            <li><b>Feat (Evolutive):</b> Aggiunto il supporto al copia e incolla di immagini e file multimediali nella finestra di controllo (Ctrl+V per sostituire, Ctrl+Shift+V per aggiungere).</li>
        </ul>
        
        <h3 style='color: #81c784;'>Versione 2.1</h3>
        <ul>
            <li><b>Feat (Evolutive):</b> Aggiunta la visualizzazione di video (MP4, AVI, MKV, ecc.) a tutto schermo.</li>
            <li><b>Feat (Evolutive):</b> Riproduzione sequenziale per code di video trascinati.</li>
            <li><b>Feat (Evolutive):</b> Fermi immagine (congelamento sull'ultimo frame alla fine del video).</li>
            <li><b>Feat (Evolutive):</b> Replay dei video al click sulla miniatura nella finestra di controllo.</li>
            <li><b>Feat (Evolutive):</b> Filtro cartelle per escludere file video quando viene trascinata una cartella (importando solo immagini).</li>
            <li><b>Fix (Correttive):</b> Aggiunto il pulsante "Pulisci tutto" (Svuota Tutto) per svuotare rapidamente la lista immagini/video.</li>
        </ul>
        
        <h3 style='color: #81c784;'>Versione 2.0</h3>
        <ul>
            <li><b>Feat (Evolutive):</b> Riprogettazione delle aree di drop dividendo tra "Aggiungi" e "Sostituisci".</li>
            <li><b>Feat (Evolutive):</b> Elenco schema delle immagini in presentazione con anteprime (thumbnails) e possibilità di eliminare singole immagini.</li>
            <li><b>Feat (Evolutive):</b> Storico sfogliabile per singole/coppie/gruppi di immagini caricate.</li>
        </ul>
        
        <h3 style='color: #81c784;'>Versione 1.0</h3>
        <ul>
            <li><b>Feat (Evolutive):</b> Supporto drag and drop di cartelle per caricare automaticamente tutte le immagini.</li>
            <li><b>Feat (Evolutive):</b> Supporto drag and drop di immagini direttamente dal browser (tramite URL o dati immagine).</li>
        </ul>
        """
        self.text_browser.setHtml(html_content)
        layout.addWidget(self.text_browser)
        
        btn_close = QPushButton("Chiudi")
        btn_close.setStyleSheet("background-color: #555; color: white; padding: 6px; border-radius: 4px;")
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close)
        
        self.setLayout(layout)

class GuideDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Guida all'uso - {__version__}")
        self.resize(450, 350)
        self.setStyleSheet("background-color: #222; color: #fff;")
        
        layout = QVBoxLayout()
        self.text_browser = QTextBrowser()
        self.text_browser.setStyleSheet("background-color: #333; color: white; border: none; font-family: sans-serif; font-size: 13px; padding: 10px;")
        
        html_content = f"""
        <h2 style='color: #4CAF50;'>Guida all'uso ({__version__})</h2>
        <p>Questo software ti permette di presentare immagini e video su un secondo schermo o in overlay in modo semplice ed elegante.</p>
        
        <h3 style='color: #e57373;'>1. Caricamento File (Drag & Drop)</h3>
        <p>Trascina immagini o file video nelle apposite aree della finestra di controllo:</p>
        <ul>
            <li><b>SOSTITUISCI:</b> Sostituisce l'intera presentazione corrente con i nuovi elementi trascinati.</li>
            <li><b>AGGIUNGI:</b> Aggiunge i nuovi elementi in coda a quelli già presenti.</li>
        </ul>
        
        <h3 style='color: #e57373;'>2. Copia e Incolla (Scorciatoie Tastiera)</h3>
        <p>Puoi copiare file da Esplora File (Ctrl+C) o immagini dal Web e incollarle premendo:</p>
        <ul>
            <li><b>Ctrl + V:</b> Sostituisce la lista corrente con gli elementi incollati.</li>
            <li><b>Ctrl + Shift + V:</b> Aggiunge gli elementi incollati in coda alla lista corrente.</li>
        </ul>
        
        <h3 style='color: #e57373;'>3. Gestione della Lista</h3>
        <ul>
            <li>Fai click sulla miniatura di un'immagine o di un video per riprodurlo.</li>
            <li>Premi il pulsante rosso <b>'X'</b> a destra di ogni riga per rimuovere quel singolo elemento.</li>
            <li>Premi il pulsante <b>'Pulisci tutto'</b> per svuotare completamente la lista.</li>
        </ul>
        
        <h3 style='color: #e57373;'>4. Modalità di Visualizzazione</h3>
        <ul>
            <li><b>TEST:</b> Mostra la finestra di visualizzazione sul lato destro dello schermo primario (con bordi normali).</li>
            <li><b>PRESENTAZIONE:</b> Visualizza a tutto schermo (senza bordi) sul secondo schermo se rilevato, altrimenti sul primario.</li>
        </ul>
        """
        self.text_browser.setHtml(html_content)
        layout.addWidget(self.text_browser)
        
        btn_close = QPushButton("Chiudi")
        btn_close.setStyleSheet("background-color: #555; color: white; padding: 6px; border-radius: 4px;")
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close)
        
        self.setLayout(layout)

class DropOverlayWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        # Sfondo semitrasparente scuro per sfocare leggermente il retro
        self.setStyleSheet("background-color: rgba(20, 20, 20, 150);")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)
        
        self.lbl_replace = QLabel("SOSTITUISCI\n\n(Rilascia qui)")
        self.lbl_replace.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_replace.setStyleSheet(
            "font-size: 16px; font-weight: bold; color: #aaa; "
            "background-color: rgba(63, 43, 43, 200); "
            "border: 3px dashed #e57373; border-radius: 12px; padding: 10px;"
        )
        
        self.lbl_add = QLabel("AGGIUNGI\n\n(Rilascia qui)")
        self.lbl_add.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_add.setStyleSheet(
            "font-size: 16px; font-weight: bold; color: #aaa; "
            "background-color: rgba(43, 63, 47, 200); "
            "border: 3px dashed #81c784; border-radius: 12px; padding: 10px;"
        )
        
        layout.addWidget(self.lbl_add)
        layout.addWidget(self.lbl_replace)
        self.setLayout(layout)
        
        self.hide()

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls() or event.mimeData().hasImage():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        pos = event.position().toPoint()
        # Controlla se la posizione è nella parte sinistra o destra
        if self.lbl_add.geometry().contains(pos):
            # Highlight Aggiungi
            self.lbl_add.setStyleSheet(
                "font-size: 16px; font-weight: bold; color: #fff; "
                "background-color: rgba(43, 85, 50, 240); "
                "border: 3px solid #81c784; border-radius: 12px; padding: 10px;"
            )
            self.lbl_replace.setStyleSheet(
                "font-size: 16px; font-weight: bold; color: #888; "
                "background-color: rgba(63, 43, 43, 150); "
                "border: 3px dashed #e57373; border-radius: 12px; padding: 10px;"
            )
        elif self.lbl_replace.geometry().contains(pos):
            # Highlight Sostituisci
            self.lbl_replace.setStyleSheet(
                "font-size: 16px; font-weight: bold; color: #fff; "
                "background-color: rgba(85, 43, 43, 240); "
                "border: 3px solid #e57373; border-radius: 12px; padding: 10px;"
            )
            self.lbl_add.setStyleSheet(
                "font-size: 16px; font-weight: bold; color: #888; "
                "background-color: rgba(43, 63, 47, 150); "
                "border: 3px dashed #81c784; border-radius: 12px; padding: 10px;"
            )
        event.acceptProposedAction()

    def dragLeaveEvent(self, event):
        # Ripristina gli stili di base e nascondi
        self.lbl_replace.setStyleSheet(
            "font-size: 16px; font-weight: bold; color: #aaa; "
            "background-color: rgba(63, 43, 43, 200); "
            "border: 3px dashed #e57373; border-radius: 12px; padding: 10px;"
        )
        self.lbl_add.setStyleSheet(
            "font-size: 16px; font-weight: bold; color: #aaa; "
            "background-color: rgba(43, 63, 47, 200); "
            "border: 3px dashed #81c784; border-radius: 12px; padding: 10px;"
        )
        self.hide()
        event.accept()

    def dropEvent(self, event):
        pos = event.position().toPoint()
        is_add = self.lbl_add.geometry().contains(pos)
        
        # Gestisci il rilascio chiamando la funzione principale della finestra di controllo
        self.parent().handle_overlay_drop(event.mimeData(), is_add)
        
        # Ripristina stili e nascondi
        self.lbl_replace.setStyleSheet(
            "font-size: 16px; font-weight: bold; color: #aaa; "
            "background-color: rgba(63, 43, 43, 200); "
            "border: 3px dashed #e57373; border-radius: 12px; padding: 10px;"
        )
        self.lbl_add.setStyleSheet(
            "font-size: 16px; font-weight: bold; color: #aaa; "
            "background-color: rgba(43, 63, 47, 200); "
            "border: 3px dashed #81c784; border-radius: 12px; padding: 10px;"
        )
        self.hide()
        event.acceptProposedAction()

class DisplayWindow(QWidget):
    playback_finished = pyqtSignal()

    def __init__(self):
        super().__init__()
        icon_path = resource_path("app_icon.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        self.pixmaps = []
        self.is_presentation_mode = False
        
        # Setup Video Widget in a Layout
        self.video_widget = QVideoWidget(self)
        self.video_widget.hide()
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.video_widget)
        self.setLayout(layout)
        
        # Setup Media Player
        self.media_player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.media_player.setAudioOutput(self.audio_output)
        self.media_player.setVideoOutput(self.video_widget)
        
        self.media_player.mediaStatusChanged.connect(self.on_media_status_changed)

    def on_media_status_changed(self, status):
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            # Freeze on the last frame by seeking slightly back and pausing
            duration = self.media_player.duration()
            if duration > 0:
                self.media_player.setPosition(max(0, duration - 100))
            self.media_player.pause()
            self.playback_finished.emit()

    def paintEvent(self, event):
        if not self.video_widget.isHidden():
            return
            
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        # Sfondo semitrasparente per entrambe le modalità (Vetro Scuro)
        dark_glass = QColor(20, 20, 20, 210)
        painter.fillRect(self.rect(), dark_glass)

        count = len(self.pixmaps)
        if count == 0:
            return

        w, h = self.width(), self.height()
        rects = []

        if count == 1:
            rects.append({'x': 0, 'y': 0, 'w': w, 'h': h})
        elif count == 2:
            rects.append({'x': 0, 'y': 0, 'w': w // 2, 'h': h})
            rects.append({'x': w // 2, 'y': 0, 'w': w // 2, 'h': h})
        elif count == 3:
            col_w = w // 3
            rects.append({'x': 0, 'y': 0, 'w': col_w, 'h': h})
            rects.append({'x': col_w, 'y': 0, 'w': col_w, 'h': h})
            rects.append({'x': col_w * 2, 'y': 0, 'w': col_w, 'h': h})
        elif count == 4:
            hw, hh = w // 2, h // 2
            rects.append({'x': 0, 'y': 0, 'w': hw, 'h': hh})
            rects.append({'x': hw, 'y': 0, 'w': hw, 'h': hh})
            rects.append({'x': 0, 'y': hh, 'w': hw, 'h': hh})
            rects.append({'x': hw, 'y': hh, 'w': hw, 'h': hh})
        else:
            # Griglia dinamica (es. 5 immagini)
            cols = math.ceil(math.sqrt(count))
            rows = math.ceil(count / cols)
            cell_w = w // cols
            cell_h = h // rows
            for i in range(count):
                row = i // cols
                col = i % cols
                rects.append({'x': col * cell_w, 'y': row * cell_h, 'w': cell_w, 'h': cell_h})

        for i, pixmap in enumerate(self.pixmaps):
            if pixmap.isNull():
                continue
            r = rects[i]
            
            pad = min(25, int(min(r['w'], r['h']) * 0.05))
            
            target_w = r['w'] - pad * 2
            target_h = r['h'] - pad * 2
            
            if target_w <= 0 or target_h <= 0:
                continue

            scaled_pixmap = pixmap.scaled(
                target_w, target_h,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            
            px = r['x'] + (r['w'] - scaled_pixmap.width()) // 2
            py = r['y'] + (r['h'] - scaled_pixmap.height()) // 2
            
            painter.drawPixmap(px, py, scaled_pixmap)

    def load_items(self, file_paths, active_index):
        self.media_player.stop()
        
        if active_index is not None and 0 <= active_index < len(file_paths):
            active_path = file_paths[active_index]
            if is_video(active_path):
                self.video_widget.show()
                self.media_player.setSource(QUrl.fromLocalFile(active_path))
                self.media_player.play()
                return
                
        self.video_widget.hide()
        image_paths = [p for p in file_paths if not is_video(p)]
        self.pixmaps = [QPixmap(path) for path in image_paths]
        self.update()

class ControlWindow(QWidget):
    images_updated = pyqtSignal(list, object) # current paths, active_index
    mode_toggled = pyqtSignal(bool) # True = Presentazione, False = Test

    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"Image Control {__version__}")
        icon_path = resource_path("app_icon.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)
        self.setAcceptDrops(True)
        self.resize(350, 500)
        self.setStyleSheet("background-color: #222;")

        self.current_image_paths = []
        self.active_index = None
        
        layout = QVBoxLayout()
        
        self.btn_mode = QPushButton("Modalità: TEST (Finestra)")
        self.btn_mode.setStyleSheet("background-color: #f44336; color: white; padding: 10px; font-weight: bold; border-radius: 5px;")
        self.btn_mode.clicked.connect(self.toggle_mode)
        layout.addWidget(self.btn_mode)
        
        # Pulsante Pulisci Tutto
        self.btn_clear = QPushButton("Pulisci tutto")
        self.btn_clear.setStyleSheet(
            "QPushButton { background-color: #555; color: white; padding: 8px; font-weight: bold; border-radius: 5px; margin-top: 10px; }"
            "QPushButton:hover { background-color: #666; }"
        )
        self.btn_clear.clicked.connect(self.clear_all)
        layout.addWidget(self.btn_clear)
        
        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet(
            "QListWidget { background-color: #333; color: white; border-radius: 5px; padding: 5px; margin-top: 10px; }"
            "QListWidget::item { border-bottom: 1px solid #444; }"
        )
        layout.addWidget(self.list_widget)

        # Footer con versione e guida "?"
        footer_layout = QHBoxLayout()
        self.btn_version = QPushButton(f"Versione {__version__}")
        self.btn_version.setStyleSheet(
            "QPushButton { color: #888; background: transparent; border: none; font-size: 11px; }"
            "QPushButton:hover { color: #fff; text-decoration: underline; }"
        )
        self.btn_version.clicked.connect(self.show_changelog)
        
        self.btn_guide = QPushButton("?")
        self.btn_guide.setFixedSize(20, 20)
        self.btn_guide.setStyleSheet(
            "QPushButton { color: #888; background: #333; border: 1px solid #555; border-radius: 10px; font-weight: bold; font-size: 11px; }"
            "QPushButton:hover { color: #fff; background: #444; }"
        )
        self.btn_guide.clicked.connect(self.show_guide)
        
        footer_layout.addWidget(self.btn_version)
        footer_layout.addStretch()
        footer_layout.addWidget(self.btn_guide)
        layout.addLayout(footer_layout)

        self.list_widget.installEventFilter(self)
        self.installEventFilter(self)

        self.overlay = DropOverlayWidget(self)

        self.setLayout(layout)
        self.is_presentation_mode = False

    def process_dropped_images(self, new_items, is_add):
        if not new_items:
            return
        
        # Separate images and videos
        images = [item for item in new_items if not is_video(item)]
        videos = [item for item in new_items if is_video(item)]
        
        # If selection is mixed (both images and videos), exclude videos
        if len(images) > 0 and len(videos) > 0:
            new_items = images
            has_new_videos = False
        else:
            has_new_videos = len(videos) > 0
            
        if not new_items:
            return

        if is_add:
            old_len = len(self.current_image_paths)
            self.current_image_paths.extend(new_items)
            if self.active_index is None and has_new_videos:
                for idx, item in enumerate(self.current_image_paths[old_len:], start=old_len):
                    if is_video(item):
                        self.active_index = idx
                        break
        else:
            self.current_image_paths = new_items.copy()
            self.active_index = None
            if has_new_videos:
                for idx, item in enumerate(self.current_image_paths):
                    if is_video(item):
                        self.active_index = idx
                        break
        
        self.refresh_list_ui()
        self.images_updated.emit(self.current_image_paths, self.active_index)

    def refresh_list_ui(self):
        self.list_widget.clear()
        for i, path in enumerate(self.current_image_paths):
            item = QListWidgetItem()
            self.list_widget.addItem(item)
            
            row_widget = QWidget()
            row_layout = QHBoxLayout()
            row_layout.setContentsMargins(5, 5, 5, 5)
            
            if i == self.active_index:
                row_widget.setStyleSheet("background-color: #3e503c; border-radius: 5px;")
            else:
                row_widget.setStyleSheet("background-color: transparent;")
            
            thumb_label = ClickableLabel()
            if is_video(path):
                thumb_label.setPixmap(create_video_thumbnail())
                thumb_label.clicked.connect(lambda idx=i: self.play_item(idx))
            else:
                pix = QPixmap(path)
                if not pix.isNull():
                    pix = pix.scaled(50, 50, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                    thumb_label.setPixmap(pix)
                thumb_label.clicked.connect(lambda: self.play_item(None))
            
            row_layout.addWidget(thumb_label)
            
            name_label = QLabel(os.path.basename(path))
            name_label.setStyleSheet("color: white;")
            name_label.setMaximumWidth(180)
            row_layout.addWidget(name_label)
            
            row_layout.addStretch()
            
            btn_del = QPushButton("X")
            btn_del.setFixedSize(24, 24)
            btn_del.setStyleSheet("background-color: #f44336; color: white; border-radius: 12px; font-weight: bold;")
            btn_del.clicked.connect(lambda checked=False, idx=i: self.delete_image(idx))
            row_layout.addWidget(btn_del)
            
            row_widget.setLayout(row_layout)
            item.setSizeHint(row_widget.sizeHint())
            self.list_widget.setItemWidget(item, row_widget)

    def clear_all(self):
        self.current_image_paths = []
        self.active_index = None
        self.refresh_list_ui()
        self.images_updated.emit(self.current_image_paths, self.active_index)

    def play_item(self, index):
        self.active_index = index
        self.refresh_list_ui()
        self.images_updated.emit(self.current_image_paths, self.active_index)

    def play_next_video(self):
        if self.active_index is None:
            return
        
        next_idx = None
        for i in range(self.active_index + 1, len(self.current_image_paths)):
            if is_video(self.current_image_paths[i]):
                next_idx = i
                break
                
        if next_idx is not None:
            self.active_index = next_idx
            self.refresh_list_ui()
            self.images_updated.emit(self.current_image_paths, self.active_index)

    def delete_image(self, index):
        if 0 <= index < len(self.current_image_paths):
            self.current_image_paths.pop(index)
            if index == self.active_index:
                next_idx = None
                for i in range(index, len(self.current_image_paths)):
                    if is_video(self.current_image_paths[i]):
                        next_idx = i
                        break
                self.active_index = next_idx
            elif self.active_index is not None and index < self.active_index:
                self.active_index -= 1
                
            self.refresh_list_ui()
            self.images_updated.emit(self.current_image_paths, self.active_index)

    def toggle_mode(self):
        self.is_presentation_mode = not self.is_presentation_mode
        if self.is_presentation_mode:
            self.btn_mode.setText("Modalità: PRESENTAZIONE (Fullscreen)")
            self.btn_mode.setStyleSheet("background-color: #4CAF50; color: white; padding: 10px; font-weight: bold; border-radius: 5px;")
        else:
            self.btn_mode.setText("Modalità: TEST (Finestra)")
            self.btn_mode.setStyleSheet("background-color: #f44336; color: white; padding: 10px; font-weight: bold; border-radius: 5px;")
        self.mode_toggled.emit(self.is_presentation_mode)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls() or event.mimeData().hasImage():
            self.overlay.setGeometry(self.rect())
            self.overlay.show()
            self.overlay.raise_()
            event.acceptProposedAction()
        else:
            event.ignore()

    def extract_items_from_mime(self, mime):
        new_items = []
        raw_image = QImage()
        loaded = False
        for fmt in ['image/png', 'image/jpeg', 'image/webp', 'image/bmp', 'image/gif']:
            if mime.hasFormat(fmt):
                raw_bytes = mime.data(fmt)
                if raw_image.loadFromData(raw_bytes):
                    loaded = True
                    print(f"[MIME] Immagine raw trovata nel formato: {fmt}")
                    break
        
        if not loaded and mime.hasImage():
            qimg = mime.imageData()
            if hasattr(qimg, 'isNull') and not qimg.isNull():
                raw_image = qimg
                loaded = True
                print("[MIME] Immagine trovata via hasImage()")

        if loaded:
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png").name
            if raw_image.save(temp_file, "PNG"):
                new_items.append(temp_file)
                return new_items

        if mime.hasUrls():
            for url in mime.urls():
                if url.isLocalFile():
                    p = url.toLocalFile()
                    if os.path.isdir(p):
                        for file in os.listdir(p):
                            if file.lower().endswith(valid_image_exts):
                                new_items.append(os.path.join(p, file))
                    else:
                        ext = os.path.splitext(p)[1].lower()
                        if ext in valid_image_exts or ext in valid_video_exts:
                            new_items.append(p)
                        
        if new_items:
            return new_items
            
        if mime.hasImage():
            image = mime.imageData()
            if hasattr(image, 'save') and not image.isNull():
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png").name
                if image.save(temp_file):
                    new_items.append(temp_file)
                    
        if new_items:
            return new_items

        img_urls = []
        if mime.hasHtml():
            html = mime.html()
            matches = re.findall(r'<img[^>]+src=["\'](.*?)["\']', html, re.IGNORECASE)
            for m in matches:
                img_urls.append(m)

        if not img_urls and mime.hasUrls():
            for url in mime.urls():
                if url.scheme() in ('http', 'https', 'data'):
                    img_urls.append(url.toString())

        for url_str in img_urls:
            url_str = url_str.replace('&amp;', '&')
            
            if url_str.startswith('data:image'):
                try:
                    header, data = url_str.split(',', 1)
                    ext = ".png"
                    if "jpeg" in header or "jpg" in header: ext = ".jpg"
                    elif "webp" in header: ext = ".webp"
                    elif "gif" in header: ext = ".gif"
                    
                    decoded = base64.b64decode(data)
                    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=ext).name
                    with open(temp_file, 'wb') as f:
                        f.write(decoded)
                    new_items.append(temp_file)
                except Exception as e:
                    print(f"Errore decodifica immagine base64: {e}")
            elif url_str.startswith('http'):
                try:
                    req = urllib.request.Request(
                        url_str, 
                        headers={
                            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                            'Accept': 'image/avif,image/webp,image/apng,image/*,*/*;q=0.8',
                            'Referer': 'https://www.google.com/'
                        }
                    )
                    with urllib.request.urlopen(req, timeout=5) as response:
                        data = response.read()
                        image = QImage()
                        if image.loadFromData(data):
                            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png").name
                            if image.save(temp_file, "PNG"):
                                new_items.append(temp_file)
                except Exception as e:
                    print(f"Errore download {url_str[:50]}: {e}")

        return new_items

    def handle_overlay_drop(self, mime, is_add):
        new_items = self.extract_items_from_mime(mime)
        if new_items:
            self.process_dropped_images(new_items, is_add)

    def dropEvent(self, event):
        self.handle_overlay_drop(event.mimeData(), is_add=False)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, 'overlay') and self.overlay.isVisible():
            self.overlay.setGeometry(self.rect())

    def paste_from_clipboard(self, is_add):
        clipboard = QApplication.clipboard()
        mime = clipboard.mimeData()
        print("[PASTE] Formati MIME in clipboard:", mime.formats())
        new_items = self.extract_items_from_mime(mime)
        if new_items:
            self.process_dropped_images(new_items, is_add)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.KeyPress:
            if event.key() == Qt.Key.Key_V and event.modifiers() & Qt.KeyboardModifier.ControlModifier:
                is_add = bool(event.modifiers() & Qt.KeyboardModifier.ShiftModifier)
                self.paste_from_clipboard(is_add)
                return True
        return super().eventFilter(obj, event)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_V and event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            is_add = bool(event.modifiers() & Qt.KeyboardModifier.ShiftModifier)
            self.paste_from_clipboard(is_add)
            event.accept()
        else:
            super().keyPressEvent(event)

    def show_changelog(self):
        dialog = ChangelogDialog(self)
        dialog.exec()

    def show_guide(self):
        dialog = GuideDialog(self)
        dialog.exec()

    def closeEvent(self, event):
        QApplication.instance().quit()
        event.accept()

def main():
    app = QApplication(sys.argv)

    display = DisplayWindow()
    control = ControlWindow()

    control.images_updated.connect(display.load_items)
    display.playback_finished.connect(control.play_next_video)

    def set_display_mode(is_presentation):
        display.is_presentation_mode = is_presentation
        display.hide()
        
        screens = QApplication.screens()
        primary = screens[0]
        
        if is_presentation:
            display.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.FramelessWindowHint)
            display.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
            target = screens[1] if len(screens) > 1 else primary
            display.setGeometry(target.geometry())
            display.showFullScreen()
        else:
            display.setWindowFlags(Qt.WindowType.Window)
            display.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
            display.showNormal() 
            
            geom = primary.geometry()
            w = geom.width() // 2
            h = geom.height() - 100
            display.setGeometry(geom.x() + geom.width() // 2 - 20, geom.y() + 50, w, h)

    set_display_mode(False)
    control.mode_toggled.connect(set_display_mode)
    
    control_geom = control.frameGeometry()
    screens = QApplication.screens()
    control_geom.moveCenter(screens[0].geometry().center())
    control.move(screens[0].geometry().left() + 50, control_geom.top())
    control.show()

    sys.exit(app.exec())

if __name__ == '__main__':
    main()
