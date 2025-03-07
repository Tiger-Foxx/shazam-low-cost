import os
import librosa
import numpy as np
import matplotlib.pyplot as plt
import json
import hashlib
import os


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class SpectrogramGenerator:
    def __init__(self, data_path):
        self.data_path = data_path

        self.output_path = os.path.join(BASE_DIR, "fingerprints")

        self.spectrogram_path = os.path.join(BASE_DIR, "spectrograms")
        if not os.path.exists(self.output_path):
            os.makedirs(self.output_path)
        if not os.path.exists(self.spectrogram_path):
            os.makedirs(self.spectrogram_path)

    def generate_spectrogram(self, audio_path):
        y, sr= librosa.load(audio_path, sr=None)
        S = librosa.feature.melspectrogram(y=y, sr=sr)
        S_DB = librosa.power_to_db(S, ref=np.max)
        return S_DB

    def extract_features(self, spectrogram):
        """
        Extract summarized audio features from a spectrogram.
        :param spectrogram: Spectrogram (assumed in dB scale).
        :return: A dictionary containing summarized features.
        """
        features = {}
        try:

            amplitude_spectrogram = librosa.db_to_amplitude(spectrogram)


            features['spectral_centroid_mean'] = float(np.mean(librosa.feature.spectral_centroid(S=amplitude_spectrogram)))
            features['spectral_bandwidth_mean'] = float(np.mean(librosa.feature.spectral_bandwidth(S=amplitude_spectrogram)))
            features['spectral_contrast_mean'] = float(np.mean(librosa.feature.spectral_contrast(S=amplitude_spectrogram)))
            features['spectral_rolloff_mean'] = float(np.mean(librosa.feature.spectral_rolloff(S=amplitude_spectrogram)))


            chroma = librosa.feature.chroma_stft(S=amplitude_spectrogram)
            tonnetz = librosa.feature.tonnetz(chroma=chroma)
            features['tonnetz_mean'] = float(np.mean(tonnetz))


            zero_crossings = librosa.feature.zero_crossing_rate(amplitude_spectrogram)
            features['zero_crossing_rate_mean'] = float(np.mean(zero_crossings))


            mfcc = librosa.feature.mfcc(S=spectrogram, n_mfcc=13)
            for i in range(mfcc.shape[0]):
                features[f'mfcc_{i}_mean'] = float(np.mean(mfcc[i, :]))

        except Exception as e:
            print(f"Error extracting features: {e}")

        return features


    def perceptual_hash(self, features):
        features_str = json.dumps(features, sort_keys=True)
        hash_object = hashlib.sha256(features_str.encode('utf-8'))
        return {
            "features": features,
            "phash": hash_object.hexdigest()
        }

    def save_fingerprint(self, fingerprint, filename):
        with open(filename, 'w') as file:
            json.dump(fingerprint, file, indent=4)

    def process_files(self):
        for team in range(1, 21):
            if team == 2 or team == 4 or team == 12:
                continue
            team_folder = os.path.join(self.data_path, f'Team_{team}')
            for file in os.listdir(team_folder):
                if file.endswith('.wav') or file.endswith('.mp3'):
                    file_path = os.path.join(team_folder, file)
                    S_DB = self.generate_spectrogram(file_path)


                    plt.figure(figsize=(10, 4))
                    librosa.display.specshow(S_DB, sr=22050, x_axis='time', y_axis='mel')
                    plt.colorbar(format='%+2.0f dB')
                    plt.title(file)
                    plt.tight_layout()
                    spectrogram_filename = os.path.join(self.spectrogram_path, f"{file}.png")
                    plt.savefig(spectrogram_filename)
                    plt.close()

                    features = self.extract_features(S_DB)
                    fingerprint = self.perceptual_hash(features)
                    fingerprint_filename = os.path.join(self.output_path, f"{file}.json")
                    self.save_fingerprint(fingerprint, fingerprint_filename)
                    print(f"Processed {file}")


