import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget,QLabel,
                             QHBoxLayout,QGridLayout,QPushButton,QSlider,QGroupBox,QTableWidget,QTableWidgetItem,QSizePolicy,QHeaderView,QFileDialog,QMessageBox)
from PyQt5.QtCore import Qt, pyqtSignal, QObject,QCoreApplication
from PyQt5.QtGui import QPixmap
import numpy as np
import os
import json
import librosa
import soundfile as sf
from generate_spectrogram import SpectrogramGenerator


class Shazam(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Shazam")
        self.setGeometry(200, 200, 1500, 1000)

        # Initialize UI components
        self.initUi()
        
        # Set the base folder for the SpectrogramGenerator
        self.base_folder = self.get_base_folder()
        
        # Initialize SpectrogramGenerator
        self.generator = SpectrogramGenerator(self.base_folder)
        
        # Generate spectrograms for all files
        # self.generate_spectrograms()

    def initUi(self):
        main_window = QWidget()
        container = QGridLayout()
        main_window.setLayout(container)
        self.setCentralWidget(main_window)

        controls = self.create_controls()
        self.table = self.create_table()

        self.song_name_label = QLabel("") # Add label for song name 
        self.song_name_label.setStyleSheet("font-size: 27px; color: white; margin: 10px; border:2px solid #e63797; padding:10px;text-align: center; ") # Style the label 
        self.song_name_label.setFixedWidth(500)
        self.song_name_label.setAlignment(Qt.AlignCenter) # Center text in the label
        self.song_name_label.setVisible(False) # Initially hide the label 

        hor_layout_label=QHBoxLayout()
        hor_layout_label.addStretch(1)
        hor_layout_label.addWidget(self.song_name_label)
        hor_layout_label.addStretch(1)

        ver_layout=QVBoxLayout()
        ver_layout.addWidget(self.table)
        ver_layout.addLayout(hor_layout_label)


        container.addWidget(controls, 0, 0)
        container.addLayout(ver_layout, 0, 1)

        container.setColumnStretch(0, 1)
        container.setColumnStretch(1, 3)
        container.setRowStretch(0, 1)

        #Styling
        self.setStyleSheet("""
            QTableWidget { 
                background-color: #2E2E2E;
                color: "white"; 
                font-size: 18px; 
                border: 1px solid #696969;
            }
            QHeaderView::section { 
                background-color: #0fc7d4; 
                color:"black"; 
                font-size: 18px; 
                border: 1px solid #696969; 
                padding: 5px;
            } 
            QTableWidget QTableCornerButton::section { 
                background-color: #0fc7d4; 
                border: 1px solid #696969;
            }
                           
            QPushButton {
                background-color:#e63797;
                border: 1px solid #696969;
                padding: 10px;
                border-radius: 8px;
                color: #FFFFFF;
                font-size: 14px;
                font-weight: bold;
            }

            QPushButton:hover {
                background-color: #e63797;
                border: 1px solid #0b1652;
            }

            QPushButton:pressed {
                background-color: #8B0000;
            }

            QGroupBox {
                font-size: 15px;
                font-weight: bold;
                color: #00FF7F;
                border: 2px solid #555;
                border-radius: 10px;
                margin-top: 10px;
            }

            QLabel {
                font-size: 18px;
                color:"white";
            }
            QLabel#mixer {
                font-size: 25px;
                color:"white";
            }

            QSlider::handle:horizontal {
                background:"pink";
                border: 2px solid rgba(0, 26, 255, 0.41);
                width: 16px;
                margin: -4px 0;
                border-radius: 8px;
            }

            QSlider::groove:horizontal {
                background: "#696969";
                height: 8px;
                border-radius: 4px;
            }
        """)


    def create_controls(self):
        group_box = QGroupBox()
        ver_layout = QVBoxLayout()

        # Load the image 
        image_path = '/Users/macbook/Documents/DSP_tasks/Task_5/images/song_icon.png'  # Replace with your actual image path 
        self.image_label = QLabel() 
        pixmap = QPixmap(image_path) 
        self.image_label.setPixmap(pixmap) 
        self.image_label.setScaledContents(True) # Scale image to fit label size
        self.image_label.setMaximumWidth(350) # Set a fixed width for the image
        self.image_label.setMaximumHeight(300) # Set a fixed width for the image

        self.upload_song_button = QPushButton("Upload")
        self.upload_song_button.clicked.connect(self.upload_song)
        self.upload_song_label = QLabel("")
    
        self.upload_first_song = QPushButton("First song")
        self.upload_first_song.clicked.connect(self.upload_first_song_file)
        self.upload_first_song_label = QLabel("")
       

        self.upload_second_song = QPushButton("Second song")
        self.upload_second_song.clicked.connect(self.upload_second_song_file)
        self.upload_second_song_label = QLabel("")
       

        slider_layout = QHBoxLayout() 
        self.weight1_label = QLabel("50% from first song ") 
        self.weight2_label = QLabel("50% from second song ")
        slider_layout.addWidget(self.weight1_label)
        slider_layout.addWidget(self.weight2_label)


        self.slider = QSlider(Qt.Horizontal)
        self.slider.setValue(50)
        self.slider.valueChanged.connect(self.update_slider_labels)
        self.slider.sliderReleased.connect(self.mix_songs)

        self.reset_button = QPushButton("Reset")
        self.reset_button.clicked.connect(self.reset)
        # self.mix_button.clicked.connect(self.mix_songs)

        song_mixer_label=QLabel("Song mixer")
        song_mixer_label.setObjectName("mixer")

        ver_layout.addWidget(self.image_label)
        ver_layout.addStretch(1)
        ver_layout.addWidget(QLabel("Upload song:"))
        ver_layout.addWidget(self.upload_song_button)
        ver_layout.addWidget(self.upload_song_label)
        ver_layout.addStretch(1)
        ver_layout.addWidget(song_mixer_label)
        ver_layout.addStretch(1)
        ver_layout.addWidget(QLabel("First song:"))
        ver_layout.addWidget(self.upload_first_song)
        ver_layout.addWidget(self.upload_first_song_label)
        ver_layout.addStretch(1)
        ver_layout.addWidget(QLabel("Second song:"))
        ver_layout.addWidget(self.upload_second_song)
        ver_layout.addWidget(self.upload_second_song_label)
        ver_layout.addStretch(1)
        ver_layout.addLayout(slider_layout)
        ver_layout.addWidget(self.slider)
        ver_layout.addStretch(1)
        ver_layout.addWidget(self.reset_button)

        group_box.setLayout(ver_layout)

        return group_box
    
    def update_slider_labels(self): 
        weight1 = self.slider.value() 
        weight2 = 100 - weight1 
        self.weight1_label.setText(f"{weight1}% from first song") 
        self.weight2_label.setText(f"{weight2}% from second song")


    def create_table(self):
        table = QTableWidget(60, 3)
        table.setHorizontalHeaderLabels(["Song Name", "Similarity Percentage", "Similarity status"])
        table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        table.horizontalHeader().setStretchLastSection(True)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)

        return table

    def upload_song(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Upload Song", "", "Audio Files (*.wav)")
        if file_path:
            self.uploaded_song_path = file_path
            song_name = os.path.splitext(os.path.basename(file_path))[0] # Remove the .wav extension
            self.upload_song_label.setText(f"{song_name} uploaded successfully")
            # self.song_name_label.setText(song_name) # Update label with file name 
            self.process_uploaded_song(file_path)

    def process_uploaded_song(self, file_path):
        S_DB = self.generator.generate_spectrogram(file_path)
        features = self.generator.extract_features(S_DB)
        uploaded_fingerprint = self.generator.perceptual_hash(features)
        similarity_scores = self.find_similar_songs(uploaded_fingerprint)
        self.update_table(similarity_scores)

    def get_song_type(self, filename):

        if 'vocals' in filename:
             return "vocals"
        
        elif 'instruments' in filename:
             return "instruments"
        
        elif 'original' in filename:
             return "original" 
        else: 
            return "Unknown"

    def find_similar_songs(self, uploaded_fingerprint):
        print(f"uploaded:{uploaded_fingerprint}")
        similarity_scores = []
        i=0
        for file in os.listdir(self.generator.output_path):
            i+=1
            if file.endswith('.json'):
                with open(os.path.join(self.generator.output_path, file), 'r') as f:
                    data = json.load(f)

                    if "features" in data:
                        print(i)
                        # fingerprint_features = data['features']
                        similarity = self.compute_similarity(uploaded_fingerprint, data)
                    else:
                        print(f"Invalid fingerprint structure in {file}: {data}")
                        continue
                    similarity_percentage = min(similarity * 100, 100)  # Convert to percentage and cap
                    similarity_scores.append((file, similarity_percentage))
        similarity_scores.sort(key=lambda x: x[1], reverse=True)  # Sort by similarity descending
        return similarity_scores

    def compute_similarity(self, fingerprint1, fingerprint2):
        def cosine_similarity(vec1, vec2):
            """
            Calculate cosine similarity for vectors.
            If inputs are scalars, calculate a simple difference-based similarity.
            """
            if isinstance(vec1, (int, float)) and isinstance(vec2, (int, float)):
                # Use inverse difference for scalars
                return 1 - abs(vec1 - vec2) / (abs(vec1) + abs(vec2) + 1e-8)
            
            # Handle vectors
            vec1 = np.array(vec1)
            vec2 = np.array(vec2)
            if vec1.ndim > 1:
                vec1 = vec1.flatten()
            if vec2.ndim > 1:
                vec2 = vec2.flatten()
            return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2) + 1e-8)

        def hamming_distance(hash1, hash2):
            """
            Calculate the Hamming distance between two perceptual hashes.
            Returns a normalized similarity score between 0 and 1.
            """
            return 1 - (sum(c1 != c2 for c1, c2 in zip(hash1, hash2)) / len(hash1))

        similarities = []

        # Define feature keys and weights
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
        # Assign weights to MFCCs
        for i in range(13):
            weights[f'mfcc_{i}_mean'] = 0.02 * (1.25 if i == 0 else 1)

        # Compute similarity for each feature
        for key in feature_keys:
            if key in fingerprint1["features"] and key in fingerprint2["features"]:
                sim = cosine_similarity(fingerprint1["features"][key], fingerprint2["features"][key])
                weight = weights.get(key, 0.05)  # Default weight for unknown keys
                similarities.append(weight * sim)

        # Compute similarity for perceptual hashes
        if "phash" in fingerprint1 and "phash" in fingerprint2:
            phash_sim = hamming_distance(fingerprint1["phash"], fingerprint2["phash"])
            phash_weight = 0.10  # Assign a weight to perceptual hash similarity
            similarities.append(phash_weight * phash_sim)

        # Aggregate similarities
        total_similarity = sum(similarities)
        return total_similarity



        
    def get_similarity_status(self, similarity):
       
        if similarity >= 80:
            return "High"
        elif similarity >= 20:
            return "Medium"
        else:
            return "Low"

    def update_table(self, similarity_scores):
        self.table.setRowCount(len(similarity_scores))
        for i, (filename, similarity) in enumerate(similarity_scores):
            song_name = filename.replace('.json', '')
            status=self.get_similarity_status(similarity)
            if i==0:
                self.song_name_label.setVisible(True) # Make the label visible
                self.song_name_label.setText(song_name[:-4])


            self.table.setItem(i, 0, QTableWidgetItem(song_name[:-4]))
            self.table.setItem(i, 1, QTableWidgetItem(f"{similarity:.2f}%"))
            self.table.setItem(i, 2, QTableWidgetItem(status))



    def upload_first_song_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select First Song", "", "Audio Files (*.wav)")
        if file_path:
            self.first_song_path = file_path
            song_name = os.path.splitext(os.path.basename(file_path))[0] # Remove the .wav extension
            self.upload_first_song_label.setText(f"{song_name} uploaded successfully")

    def upload_second_song_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Second Song", "", "Audio Files (*.wav)")
        if file_path:
            self.second_song_path = file_path
            song_name = os.path.splitext(os.path.basename(file_path))[0] # Remove the .wav extension
            self.upload_second_song_label.setText(f"{song_name} uploaded successfully")

    def mix_songs(self):
        if hasattr(self, 'first_song_path') and hasattr(self, 'second_song_path'):
            # Load the songs
            y1, sr1 = librosa.load(self.first_song_path, sr=None)
            y2, sr2 = librosa.load(self.second_song_path, sr=None)

            # Resample if the sample rates don't match
            if sr1 != sr2:
                sr_common = min(sr1, sr2)
                y1 = librosa.resample(y1, orig_sr=sr1, target_sr=sr_common) 
                y2 = librosa.resample(y2, orig_sr=sr2, target_sr=sr_common) 
                sr1 = sr_common

            # Truncate the longer array to match the shorter array's length 
            min_length = min(len(y1), len(y2)) 
            y1 = y1[:min_length] 
            y2 = y2[:min_length]
            
            # Get the slider value range [0, 1]
            mix_ratio = self.slider.value() / 100.0

            # Mix the songs: y_mixed = (1 - mix_ratio) * y1 + mix_ratio * y2
            y_mixed = (1 - mix_ratio) * y2 + mix_ratio * y1
            y_mixed /= np.max(np.abs(y_mixed))  # Normalize to avoid clipping

            # Ensure output directory exists
            mixed_song_path = '/Users/macbook/Documents/DSP_tasks/Task_5/mixed_song'
            if not os.path.exists(mixed_song_path):
                os.makedirs(mixed_song_path)
            
            # Save the mixed song
            mixed_song_file = os.path.join(mixed_song_path, 'mixed_song.wav')
            sf.write(mixed_song_file, y_mixed, sr1)
            # QMessageBox.information(self, "Success", f"Mixed song saved as: {mixed_song_file}")
            self.song_name_label.setVisible(False) # Hide label when mixing songs

            # Process the mixed song to find the closest matches
            self.process_uploaded_song(mixed_song_file)

        else:
            QMessageBox.warning(self, "Error", "Please upload both songs before mixing.")


    def generate_spectrograms(self):
        self.generator.process_files()

    def get_base_folder(self):
        return '/Users/macbook/Documents/DSP_tasks/Task_5/Task _5_ Data'  # Path to the folder containing the team folders

    def reset(self):
        self.initUi()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Shazam()
    window.show()
    sys.exit(app.exec_())
