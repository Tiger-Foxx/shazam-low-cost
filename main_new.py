import sys
import os
import json
import numpy as np
import librosa
import soundfile as sf
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QPushButton, QSlider,
    QFileDialog, QMessageBox, QVBoxLayout, QHBoxLayout, QGridLayout,
    QTableWidget, QTableWidgetItem, QFrame, QProgressBar, QGraphicsDropShadowEffect,
    QSizePolicy, QHeaderView, QSpacerItem
)
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, QTimer, QSize, pyqtSignal
from PyQt5.QtGui import QPixmap, QFont, QColor, QPalette, QIcon, QFontDatabase
from generate_spectrogram import SpectrogramGenerator

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

COLORS = {
    "background": "#121212",
    "card": "#1E1E1E",
    "primary": "#2962FF",
    "secondary": "#0091EA",
    "text_primary": "#EEEEEE",
    "text_secondary": "#B0B0B0",
    "success": "#00C853",
    "warning": "#FFD600",
    "error": "#FF1744",
    "hover": "#3D3D3D",
    "pressed": "#000000",
    "border": "#333333",
    "disabled": "#666666"
}


class ModernButton(QPushButton):
    """Bouton stylisé avec effet de survol et d'appui"""

    def __init__(self, text, icon=None, color=COLORS["primary"]):
        super().__init__(text)
        self.setMinimumHeight(40)
        self.color = color
        self.setCursor(Qt.PointingHandCursor)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 2)
        self.setGraphicsEffect(shadow)

        if icon:
            self.setIcon(icon)
            self.setIconSize(QSize(20, 20))

        self.apply_style()

    def apply_style(self):
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.color};
                color: {COLORS["text_primary"]};
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: {QColor(self.color).lighter(115).name()};
            }}
            QPushButton:pressed {{
                background-color: {QColor(self.color).darker(115).name()};
            }}
            QPushButton:disabled {{
                background-color: {COLORS["disabled"]};
                color: {COLORS["text_secondary"]};
            }}
        """)


class ModernSlider(QSlider):
    """Slider stylisé avec des animations fluides"""

    def __init__(self, orientation=Qt.Horizontal):
        super().__init__(orientation)
        self.setMinimumHeight(30)
        self.setStyleSheet(f"""
            QSlider::groove:horizontal {{
                height: 8px;
                background: {COLORS["card"]};
                border-radius: 4px;
            }}
            QSlider::handle:horizontal {{
                background: {COLORS["primary"]};
                border: none;
                width: 18px;
                height: 18px;
                margin: -5px 0;
                border-radius: 9px;
            }}
            QSlider::sub-page:horizontal {{
                background: {COLORS["secondary"]};
                border-radius: 4px;
            }}
        """)


class ModernTableWidget(QTableWidget):
    """Tableau stylisé avec des lignes alternées et animations de survol"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setStyleSheet(f"""
            QTableWidget {{
                background-color: {COLORS["card"]};
                color: {COLORS["text_primary"]};
                gridline-color: {COLORS["border"]};
                border-radius: 10px;
                border: none;
                padding: 5px;
                font-size: 14px;
            }}
            QTableWidget::item {{
                padding: 10px;
                border-radius: 5px;
            }}
            QTableWidget::item:selected {{
                background-color: {COLORS["primary"]};
                color: {COLORS["text_primary"]};
            }}
            QTableWidget::item:hover {{
                background-color: {COLORS["hover"]};
            }}
            QHeaderView::section {{
                background-color: {COLORS["secondary"]};
                color: {COLORS["text_primary"]};
                padding: 12px;
                border: none;
                font-weight: bold;
                font-size: 15px;
                border-radius: 5px;
                margin: 2px;
            }}
            QScrollBar:vertical {{
                border: none;
                background: {COLORS["card"]};
                width: 10px;
                border-radius: 5px;
            }}
            QScrollBar::handle:vertical {{
                background: {COLORS["secondary"]};
                border-radius: 5px;
                min-height: 20px;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
        """)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 4)
        self.setGraphicsEffect(shadow)


class CircularProgressBar(QProgressBar):
    """Barre de progression circulaire pour indiquer le chargement"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(150, 150)
        self.setMaximumSize(150, 150)
        self.setValue(0)
        self.setTextVisible(True)
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet(f"""
            QProgressBar {{
                border: none;
                border-radius: 75px;
                background-color: {COLORS["card"]};
                color: {COLORS["text_primary"]};
                font-weight: bold;
                font-size: 18px;
            }}
            QProgressBar::chunk {{
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                                stop:0 {COLORS["primary"]},
                                                stop:1 {COLORS["secondary"]});
                border-radius: 75px;
            }}
        """)


class Card(QFrame):
    """Conteneur stylisé avec bordure arrondie et ombre"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.StyledPanel)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS["card"]};
                border-radius: 15px;
                border: 1px solid {COLORS["border"]};
            }}
        """)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 120))
        shadow.setOffset(0, 5)
        self.setGraphicsEffect(shadow)


class LoadingOverlay(QWidget):
    """Overlay de chargement avec animation pendant les opérations longues"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        self.loader = CircularProgressBar()
        layout.addWidget(self.loader)

        self.label = QLabel("Traitement en cours...")
        self.label.setStyleSheet(f"color: {COLORS['text_primary']}; font-size: 16px; font-weight: bold;")
        self.label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label)

        self.hide()

    def showEvent(self, event):
        super().showEvent(event)
        self.loader.setValue(0)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateProgress)
        self.timer.start(30)

    def updateProgress(self):
        value = self.loader.value()
        if value >= 100:
            self.loader.setValue(0)
        else:
            self.loader.setValue(value + 1)

    def setMessage(self, message):
        self.label.setText(message)


class ModernLabel(QLabel):
    """Label stylisé avec police moderne et espacement"""

    def __init__(self, text="", is_title=False, is_subtitle=False):
        super().__init__(text)

        font_size = 24 if is_title else 18 if is_subtitle else 14
        font_weight = "bold" if is_title or is_subtitle else "normal"

        self.setStyleSheet(f"""
            QLabel {{
                color: {COLORS["text_primary"]};
                font-size: {font_size}px;
                font-weight: {font_weight};
                margin: 5px;
            }}
        """)

        if is_title:
            self.setAlignment(Qt.AlignCenter)


class Shazam(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Shazam • Reconnaissance Musicale")
        self.setGeometry(100, 100, 1280, 800)
        self.setStyleSheet(f"background-color: {COLORS['background']};")
        icon_path = os.path.join(BASE_DIR, "images", "SH.png")
        self.setWindowIcon(QIcon(icon_path))

        self.uploaded_song_path = None
        self.first_song_path = None
        self.second_song_path = None
        self.animation_group = None

        self.setupUi()

        self.base_folder = self.get_base_folder()
        self.generator = SpectrogramGenerator(self.base_folder)

        self.loading_overlay = LoadingOverlay(self)
        self.loading_overlay.resize(self.size())

    def setupUi(self):

        central_widget = QWidget()
        main_layout = QGridLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        self.setCentralWidget(central_widget)

        self.control_panel = self.setupControlPanel()

        self.results_panel = self.setupResultsPanel()

        main_layout.addWidget(self.control_panel, 0, 0)
        main_layout.addWidget(self.results_panel, 0, 1)

        main_layout.setColumnStretch(0, 1)
        main_layout.setColumnStretch(1, 2)

    def setupControlPanel(self):

        panel = Card()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        title = ModernLabel("SHAZAM", is_title=True)
        layout.addWidget(title)

        logo_container = QWidget()
        logo_layout = QHBoxLayout(logo_container)
        logo_layout.setAlignment(Qt.AlignCenter)

        image_path = os.path.join(BASE_DIR, "images", "SH.png")
        self.logo_label = QLabel()
        pixmap = QPixmap(image_path)
        self.logo_label.setPixmap(pixmap.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.logo_label.setAlignment(Qt.AlignCenter)

        logo_layout.addWidget(self.logo_label)
        layout.addWidget(logo_container)

        recognition_label = ModernLabel("Reconnaissance de chanson", is_subtitle=True)
        layout.addWidget(recognition_label)

        self.upload_song_button = ModernButton("Sélectionner un fichier audio", color=COLORS["primary"])
        self.upload_song_button.clicked.connect(self.upload_song)
        layout.addWidget(self.upload_song_button)

        self.upload_song_label = ModernLabel("")
        layout.addWidget(self.upload_song_label)

        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet(f"background-color: {COLORS['border']}; max-height: 1px;")
        layout.addWidget(separator)

        mixer_label = ModernLabel("Mixage de chansons", is_subtitle=True)
        layout.addWidget(mixer_label)

        self.upload_first_song_button = ModernButton("Première chanson", color=COLORS["secondary"])
        self.upload_first_song_button.clicked.connect(self.upload_first_song_file)
        layout.addWidget(self.upload_first_song_button)

        self.upload_first_song_label = ModernLabel("")
        layout.addWidget(self.upload_first_song_label)

        self.upload_second_song_button = ModernButton("Deuxième chanson", color=COLORS["secondary"])
        self.upload_second_song_button.clicked.connect(self.upload_second_song_file)
        layout.addWidget(self.upload_second_song_button)

        self.upload_second_song_label = ModernLabel("")
        layout.addWidget(self.upload_second_song_label)

        slider_container = QWidget()
        slider_layout = QVBoxLayout(slider_container)

        slider_labels_layout = QHBoxLayout()
        self.weight1_label = ModernLabel("50% première chanson")
        self.weight2_label = ModernLabel("50% deuxième chanson")

        slider_labels_layout.addWidget(self.weight1_label)
        slider_labels_layout.addStretch()
        slider_labels_layout.addWidget(self.weight2_label)

        self.mixer_slider = ModernSlider(Qt.Horizontal)
        self.mixer_slider.setValue(50)
        self.mixer_slider.valueChanged.connect(self.update_slider_labels)
        self.mixer_slider.sliderReleased.connect(self.mix_songs)

        slider_layout.addLayout(slider_labels_layout)
        slider_layout.addWidget(self.mixer_slider)

        layout.addWidget(slider_container)

        self.reset_button = ModernButton("Réinitialiser", color=COLORS["error"])
        self.reset_button.clicked.connect(self.reset)
        layout.addWidget(self.reset_button)

        layout.addStretch()

        return panel

    def setupResultsPanel(self):

        panel = Card()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        title = ModernLabel("Résultats de la recherche", is_title=True)
        layout.addWidget(title)

        self.song_name_card = Card()
        song_name_layout = QVBoxLayout(self.song_name_card)

        recognition_label = ModernLabel("Chanson détectée:", is_subtitle=True)
        recognition_label.setAlignment(Qt.AlignCenter)
        song_name_layout.addWidget(recognition_label)

        self.song_name_label = ModernLabel("")
        self.song_name_label.setAlignment(Qt.AlignCenter)
        self.song_name_label.setStyleSheet(f"""
            color: {COLORS["primary"]};
            font-size: 28px;
            font-weight: bold;
            padding: 15px;
        """)
        song_name_layout.addWidget(self.song_name_label)

        layout.addWidget(self.song_name_card)
        self.song_name_card.hide()

        table_label = ModernLabel("Correspondances similaires:", is_subtitle=True)
        layout.addWidget(table_label)

        self.results_table = ModernTableWidget(0, 3)
        self.results_table.setHorizontalHeaderLabels(["Titre de la chanson", "Pourcentage de similarité", "Statut"])
        self.results_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.results_table.verticalHeader().setVisible(False)
        self.results_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.results_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.results_table.setAlternatingRowColors(True)
        self.results_table.setStyleSheet(self.results_table.styleSheet() + f"""
            QTableWidget::item:alternate {{
                background-color: {COLORS["hover"]};
            }}
        """)

        layout.addWidget(self.results_table)

        return panel

    def update_slider_labels(self):
        weight1 = self.mixer_slider.value()
        weight2 = 100 - weight1
        self.weight1_label.setText(f"{weight1}% première chanson")
        self.weight2_label.setText(f"{weight2}% deuxième chanson")

    def upload_song(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Sélectionner un fichier audio", "", "Fichiers audio (*.wav)"
        )

        if file_path:
            self.uploaded_song_path = file_path
            song_name = os.path.splitext(os.path.basename(file_path))[0]
            self.upload_song_label.setText(f"'{song_name}' chargé avec succès")

            self.loading_overlay.resize(self.size())
            self.loading_overlay.setMessage("Analyse en cours...")
            self.loading_overlay.show()

            QTimer.singleShot(100, lambda: self.process_uploaded_song(file_path))

    def process_uploaded_song(self, file_path):
        try:

            S_DB = self.generator.generate_spectrogram(file_path)
            features = self.generator.extract_features(S_DB)
            uploaded_fingerprint = self.generator.perceptual_hash(features)

            similarity_scores = self.find_similar_songs(uploaded_fingerprint)

            QTimer.singleShot(500, lambda: self.update_table(similarity_scores))

        except Exception as e:
            self.loading_overlay.hide()
            QMessageBox.critical(self, "Erreur", f"Une erreur s'est produite lors du traitement: {str(e)}")

    def find_similar_songs(self, uploaded_fingerprint):
        similarity_scores = []

        for file in os.listdir(self.generator.output_path):
            if file.endswith('.json'):
                try:
                    with open(os.path.join(self.generator.output_path, file), 'r') as f:
                        data = json.load(f)

                    if "features" in data:
                        similarity = self.compute_similarity(uploaded_fingerprint, data)
                        similarity_percentage = min(similarity * 100, 100)
                        similarity_scores.append((file, similarity_percentage))
                    else:
                        print(f"Structure d'empreinte invalide dans {file}: {data}")
                        continue

                except Exception as e:
                    print(f"Erreur lors du traitement de {file}: {str(e)}")

        similarity_scores.sort(key=lambda x: x[1], reverse=True)

        return similarity_scores

    def compute_similarity(self, fingerprint1, fingerprint2):
        def cosine_similarity(vec1, vec2):
            """
            Calculer la similarité cosinus pour les vecteurs.
            Si les entrées sont des scalaires, calculer une similarité basée sur la différence.
            """
            if isinstance(vec1, (int, float)) and isinstance(vec2, (int, float)):
                return 1 - abs(vec1 - vec2) / (abs(vec1) + abs(vec2) + 1e-8)

            vec1 = np.array(vec1)
            vec2 = np.array(vec2)
            if vec1.ndim > 1:
                vec1 = vec1.flatten()
            if vec2.ndim > 1:
                vec2 = vec2.flatten()
            return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2) + 1e-8)

        def hamming_distance(hash1, hash2):
            """
            Calculer la distance de Hamming entre deux hachages perceptuels.
            Retourne un score de similarité normalisé entre 0 et 1.
            """
            return 1 - (sum(c1 != c2 for c1, c2 in zip(hash1, hash2)) / len(hash1))

        similarities = []

        feature_keys = ["spectral_centroid_mean", "spectral_bandwidth_mean", "spectral_contrast_mean",
                        "spectral_rolloff_mean", "tonnetz_mean", "zero_crossing_rate_mean"]
        mfcc_keys = [f'mfcc_{i}_mean' for i in range(13)]
        feature_keys.extend(mfcc_keys)

        weights = {
            "spectral_centroid_mean": 0.15,
            "spectral_bandwidth_mean": 0.10,
            "spectral_contrast_mean": 0.10,
            "spectral_rolloff_mean": 0.10,
            "tonnetz_mean": 0.15,
            "zero_crossing_rate_mean": 0.10
        }

        for i in range(13):
            weights[f'mfcc_{i}_mean'] = 0.02 * (1.25 if i == 0 else 1)

        for key in feature_keys:
            if key in fingerprint1["features"] and key in fingerprint2["features"]:
                sim = cosine_similarity(fingerprint1["features"][key], fingerprint2["features"][key])
                weight = weights.get(key, 0.05)
                similarities.append(weight * sim)

        if "phash" in fingerprint1 and "phash" in fingerprint2:
            phash_sim = hamming_distance(fingerprint1["phash"], fingerprint2["phash"])
            phash_weight = 0.10
            similarities.append(phash_weight * phash_sim)

        total_similarity = sum(similarities)
        return total_similarity

    def get_similarity_status(self, similarity):
        if similarity >= 80:
            return ("Élevée", COLORS["success"])
        elif similarity >= 20:
            return ("Moyenne", COLORS["warning"])
        else:
            return ("Faible", COLORS["error"])

    def update_table(self, similarity_scores):

        self.loading_overlay.hide()

        self.results_table.setRowCount(len(similarity_scores))

        for i, (filename, similarity) in enumerate(similarity_scores):

            song_name = filename.replace('.json', '')
            song_name = song_name[:-4] if song_name.endswith('_out') else song_name

            status, color = self.get_similarity_status(similarity)

            song_item = QTableWidgetItem(song_name)
            similarity_item = QTableWidgetItem(f"{similarity:.2f}%")
            status_item = QTableWidgetItem(status)

            song_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            similarity_item.setTextAlignment(Qt.AlignCenter)
            status_item.setTextAlignment(Qt.AlignCenter)

            status_item.setForeground(QColor(color))

            self.results_table.setItem(i, 0, song_item)
            self.results_table.setItem(i, 1, similarity_item)
            self.results_table.setItem(i, 2, status_item)

            if i == 0:
                self.song_name_card.show()

                self.song_name_label.setText(song_name)

                self.animate_recognition_result()

    def animate_recognition_result(self):

        self.song_name_card.setGraphicsEffect(None)
        effect = QGraphicsDropShadowEffect()
        effect.setBlurRadius(20)
        effect.setColor(QColor(COLORS["primary"]))
        effect.setOffset(0, 0)
        self.song_name_card.setGraphicsEffect(effect)

        animation = QPropertyAnimation(effect, b"blurRadius")
        animation.setDuration(1500)
        animation.setStartValue(5)
        animation.setEndValue(20)
        animation.setEasingCurve(QEasingCurve.InOutQuad)
        animation.start()

    def upload_first_song_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Sélectionner la première chanson", "", "Fichiers audio (*.wav)"
        )

        if file_path:
            self.first_song_path = file_path
            song_name = os.path.splitext(os.path.basename(file_path))[0]
            self.upload_first_song_label.setText(f"'{song_name}' chargé avec succès")

    def upload_second_song_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Sélectionner la deuxième chanson", "", "Fichiers audio (*.wav)"
        )

        if file_path:
            self.second_song_path = file_path
            song_name = os.path.splitext(os.path.basename(file_path))[0]
            self.upload_second_song_label.setText(f"'{song_name}' chargé avec succès")

    def mix_songs(self):
        if not hasattr(self, 'first_song_path') or not hasattr(self, 'second_song_path'):
            QMessageBox.warning(self, "Attention", "Veuillez d'abord charger les deux chansons à mixer.")
            return

        self.loading_overlay.resize(self.size())
        self.loading_overlay.setMessage("Mixage en cours...")
        self.loading_overlay.show()

        QTimer.singleShot(100, self._mix_songs_process)

    def _mix_songs_process(self):
        try:

            y1, sr1 = librosa.load(self.first_song_path, sr=None)
            y2, sr2 = librosa.load(self.second_song_path, sr=None)

            if sr1 != sr2:
                sr_common = min(sr1, sr2)
                y1 = librosa.resample(y1, orig_sr=sr1, target_sr=sr_common)
                y2 = librosa.resample(y2, orig_sr=sr2, target_sr=sr_common)
                sr1 = sr_common

            min_length = min(len(y1), len(y2))
            y1 = y1[:min_length]
            y2 = y2[:min_length]

            mix_ratio = self.mixer_slider.value() / 100.0
            y_mixed = (1 - mix_ratio) * y2 + mix_ratio * y1
            y_mixed /= np.max(np.abs(y_mixed))

            mixed_song_path = os.path.join(BASE_DIR, "mixed_songs")
            os.makedirs(mixed_song_path, exist_ok=True)

            mixed_file = os.path.join(mixed_song_path, 'mixage_resultat.wav')
            sf.write(mixed_file, y_mixed, sr1)

            QTimer.singleShot(100, lambda: self.process_uploaded_song(mixed_file))

        except Exception as e:
            self.loading_overlay.hide()
            QMessageBox.critical(self, "Erreur", f"Échec du mixage : {str(e)}")
        finally:

            QTimer.singleShot(500, self.loading_overlay.hide)

    def get_base_folder(self):
        return os.path.join(BASE_DIR, "Task_5_Data")

    def reset(self):

        self.uploaded_song_path = None
        self.first_song_path = None
        self.second_song_path = None

        self.upload_song_label.setText("")
        self.upload_first_song_label.setText("")
        self.upload_second_song_label.setText("")

        self.mixer_slider.setValue(50)
        self.update_slider_labels()

        self.results_table.setRowCount(0)
        self.song_name_card.hide()

        self.animate_reset()

    def animate_reset(self):

        effect = QGraphicsDropShadowEffect()
        effect.setColor(QColor(COLORS["error"]))
        self.song_name_card.setGraphicsEffect(effect)

        animation = QPropertyAnimation(effect, b"blurRadius")
        animation.setDuration(800)
        animation.setStartValue(0)
        animation.setEndValue(30)
        animation.setEasingCurve(QEasingCurve.OutCubic)
        animation.start()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    QFontDatabase.addApplicationFont(os.path.join(BASE_DIR, "fonts", "Roboto-Medium.ttf"))
    app.setFont(QFont("Roboto", 12))

    window = Shazam()
    window.show()
    sys.exit(app.exec_())