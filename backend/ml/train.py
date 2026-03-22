import pandas as pd
import numpy as np
import joblib
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, confusion_matrix, ConfusionMatrixDisplay
from sklearn.preprocessing import LabelEncoder
from xgboost import XGBClassifier
from imblearn.over_sampling import SMOTE

from prepare_data import load_and_prepare, get_features_and_target

# ── 1. Load & Prepare ────────────────────────────────────────
print("📦 Loading data...")
df = load_and_prepare("../data/raw/your_dataset.csv")
X, y = get_features_and_target(df)

print(f"✅ Dataset shape: {X.shape}")
print(f"✅ Class distribution:\n{y.value_counts()}")

# ── 2. Handle Class Imbalance ────────────────────────────────
# (If one class has far more samples than others)
smote = SMOTE(random_state=42)
X_balanced, y_balanced = smote.fit_resample(X, y)
print(f"✅ After SMOTE: {pd.Series(y_balanced).value_counts().to_dict()}")

# ── 3. Train/Test Split ──────────────────────────────────────
X_train, X_test, y_train, y_test = train_test_split(
    X_balanced, y_balanced,
    test_size=0.2,
    random_state=42,
    stratify=y_balanced
)

# ── 4. Train XGBoost ─────────────────────────────────────────
print("\n🚀 Training XGBoost model...")
model = XGBClassifier(
    n_estimators=200,
    max_depth=6,
    learning_rate=0.1,
    subsample=0.8,
    colsample_bytree=0.8,
    use_label_encoder=False,
    eval_metric='mlogloss',
    random_state=42
)

model.fit(
    X_train, y_train,
    eval_set=[(X_test, y_test)],
    verbose=50
)

# ── 5. Evaluate ──────────────────────────────────────────────
print("\n📊 Evaluation Results:")
y_pred = model.predict(X_test)
print(classification_report(
    y_test, y_pred,
    target_names=['LOW 🟢', 'MEDIUM 🟡', 'HIGH 🔴']
))

# Cross-validation score
cv_scores = cross_val_score(model, X_balanced, y_balanced, cv=5)
print(f"✅ Cross-val Accuracy: {cv_scores.mean():.2f} ± {cv_scores.std():.2f}")

# ── 6. Confusion Matrix ──────────────────────────────────────
cm = confusion_matrix(y_test, y_pred)
disp = ConfusionMatrixDisplay(cm, display_labels=['LOW', 'MEDIUM', 'HIGH'])
disp.plot(cmap='Blues')
plt.title('CrowdRoute — Confusion Matrix')
plt.tight_layout()
plt.savefig("../data/confusion_matrix.png")
print("✅ Confusion matrix saved!")

# ── 7. Feature Importance ────────────────────────────────────
feat_importance = pd.Series(
    model.feature_importances_,
    index=X.columns
).sort_values(ascending=False)

print(f"\n🔍 Feature Importances:\n{feat_importance}")

# ── 8. Save Model ────────────────────────────────────────────
joblib.dump(model, "saved_models/crowd_model.joblib")
joblib.dump(list(X.columns), "saved_models/feature_columns.joblib")
print("\n✅ Model saved to saved_models/crowd_model.joblib")