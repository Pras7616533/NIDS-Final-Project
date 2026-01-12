import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler

# ================================
# Correct NSL-KDD Column Names
# (INCLUDING difficulty column)
# ================================

columns = [
    'duration','protocol_type','service','flag','src_bytes','dst_bytes',
    'land','wrong_fragment','urgent','hot','num_failed_logins',
    'logged_in','num_compromised','root_shell','su_attempted','num_root',
    'num_file_creations','num_shells','num_access_files','num_outbound_cmds',
    'is_host_login','is_guest_login','count','srv_count','serror_rate',
    'srv_serror_rate','rerror_rate','srv_rerror_rate','same_srv_rate',
    'diff_srv_rate','srv_diff_host_rate','dst_host_count','dst_host_srv_count',
    'dst_host_same_srv_rate','dst_host_diff_srv_rate',
    'dst_host_same_src_port_rate','dst_host_srv_diff_host_rate',
    'dst_host_serror_rate','dst_host_srv_serror_rate',
    'dst_host_rerror_rate','dst_host_srv_rerror_rate',
    'label','difficulty'
]

# ================================
# Load Dataset
# ================================

df = pd.read_csv("data/raw/KDDTrain+.txt", names=columns)

# ================================
# Drop difficulty column (NOT a feature)
# ================================

df.drop('difficulty', axis=1, inplace=True)

# ================================
# Binary Label Encoding
# ================================

df['label'] = df['label'].apply(lambda x: 0 if x == 'normal' else 1)

# ================================
# One-Hot Encode categorical features
# ================================

categorical_cols = ['protocol_type', 'service', 'flag']
df = pd.get_dummies(df, columns=categorical_cols)

# ================================
# Split X and y
# ================================

X = df.drop('label', axis=1)
y = df['label']

# ================================
# SAFETY CHECK (VERY IMPORTANT)
# ================================

non_numeric = X.select_dtypes(include=['object']).columns
print("Non-numeric columns:", non_numeric.tolist())

# ================================
# Scaling
# ================================

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# ================================
# Save processed data
# ================================

np.save("data/processed/X.npy", X_scaled)
np.save("data/processed/y.npy", y.values)

print("✅ Preprocessing completed successfully")
print("X shape:", X_scaled.shape)
print("y shape:", y.shape)
