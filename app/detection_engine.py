import numpy as np
import random
import joblib
import os
from tensorflow.keras.models import load_model
from ips_module import IPSModule

class DetectionEngine:
    """
    Integrates deep learning models with the IPS module.
    """
    def __init__(self, models_dict):
        self.models = models_dict
        self.ips = IPSModule()
        self.scaler = self._load_scaler()
        self.feature_names = None

    def _load_scaler(self):
        scaler_path = "models/scaler.pkl"
        if os.path.exists(scaler_path):
            try:
                return joblib.load(scaler_path)
            except Exception as e:
                print(f"Error loading scaler: {e}")
        return None

    def scale_features(self, features):
        if self.scaler:
            # Assuming features is a 1D or 2D array
            if len(features.shape) == 1:
                return self.scaler.transform(features.reshape(1, -1))[0]
            else:
                return self.scaler.transform(features)
        return features

    def predict_and_prevent(self, model_name, features, remote_ip=None):
        """
        Runs prediction and triggers IPS if an attack is detected.
        
        :param model_name: Name of the model to use (DNN, CNN, LSTM, AUTOENCODER)
        :param features: Numpy array of features
        :param remote_ip: IP address of the traffic source (simulated if None)
        :return: Dict containing prediction, confidence, and action taken
        """
        if remote_ip is None:
            # Simulate an IP for demo purposes if not provided
            remote_ip = f"192.168.1.{random.randint(10, 250)}"

        model = self.models.get(model_name)
        if not model:
            return {"error": f"Model {model_name} not found"}

        # Reshape for CNN/LSTM if necessary (assuming features is a 1D array for one sample)
        x = features.copy()
        if model_name in ["CNN", "LSTM"]:
            if len(x.shape) == 1:
                x = x.reshape(1, x.shape[0], 1)
            else:
                x = x.reshape(x.shape[0], x.shape[1], 1)
        elif len(x.shape) == 1:
            x = x.reshape(1, x.shape[0])

        # Prediction logic
        if model_name == "AUTOENCODER":
            recon = model.predict(x)
            mse = np.mean(np.square(x - recon))
            prediction = "Attack" if mse > 0.01 else "Normal"
            confidence = round(1 - float(mse), 4)
        else:
            pred = model.predict(x)
            class_id = int(np.argmax(pred))
            prediction = "Normal" if class_id == 0 else "Attack"
            confidence = round(float(np.max(pred)), 4)

        # Trigger IPS if Attack
        action = "None"
        if prediction == "Attack":
            action = self.ips.handle_detection(remote_ip, f"{model_name} Predicted Attack")

        return {
            "model": model_name,
            "prediction": prediction,
            "confidence": confidence,
            "attacker_ip": remote_ip,
            "action_taken": action
        }

    def unblock_ip(self, ip):
        return self.ips.unblock_attacker(ip)

    def get_ips_status(self):
        return self.ips.get_status()
