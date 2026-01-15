import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import train_test_split

# 1. Load Data
print("Loading Three Pillars Dataset...")
df = pd.read_csv('../../data/processed/Three_Pillars_Dataset.csv', index_col=0, parse_dates=True)

# 2. Define Regimes (The Scenarios)
# We define a "Bull" week as >2% return, "Bear" as <-2%, else Neutral
df['weekly_return'] = df['XBTUSD'].pct_change(7).shift(-7)
df = df.dropna()

def categorize_regime(x):
    if x > 0.02: return 'Bull'
    elif x < -0.02: return 'Bear'
    else: return 'Neutral'

df['regime'] = df['weekly_return'].apply(categorize_regime)

# 3. Prepare Features (X) and Target (y)
# Drop future-looking columns to prevent data leakage
X = df.drop(columns=['weekly_return', 'regime'])
y = df['regime']

# 4. Train Model
# We use a standard Random Forest to simulate the "Black Box" performance
print("Training Scenario Classification Model...")
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)

clf = RandomForestClassifier(n_estimators=100, max_depth=5, random_state=42)
clf.fit(X_train, y_train)
y_pred = clf.predict(X_test)

# 5. Generate Confusion Matrix
labels = ['Bear', 'Neutral', 'Bull']
cm = confusion_matrix(y_test, y_pred, labels=labels)

# 6. Visualization
plt.figure(figsize=(8, 6))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
            xticklabels=['Pred Bear', 'Pred Neutral', 'Pred Bull'],
            yticklabels=['True Bear', 'True Neutral', 'True Bull'])
plt.title('Confusion Matrix: Scenario Analysis\n(Model Performance by Regime)', fontsize=14)
plt.ylabel('Actual Scenario')
plt.xlabel('Predicted Scenario')
plt.tight_layout()

# Save
output_file = '../../data/outputs/images/confusion_matrix.png'
plt.savefig(output_file)
print(f"SUCCESS! Confusion Matrix saved to '{output_file}'")