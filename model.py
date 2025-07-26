import joblib
import pandas as pd

# 1) Map your lowercase form fields → the exact model‑fit column names
FEATURE_MAP = {
    "nitrogen":   "Nitrogen",
    "phosphorus": "Phosphorus",
    "potassium":  "Potassium",
    "temperature":"Temperature",
    "humidity":   "Humidity",
    "ph":         "pH_Value",   # updated here
    "rainfall":   "Rainfall",
}

# 2) Load the pipeline you exported (expects those exact column names)
pipe = joblib.load("crop_pipeline.joblib")

def predict_crop(input_dict: dict) -> str:
    """
    input_dict keys are the lowercase form names.
    We reorder & rename columns so the pipeline sees:
      ["Nitrogen","Phosphorus",...,"pH_Value","Rainfall"]
    """
    # Build a one‑row DataFrame from the raw input
    df = pd.DataFrame([input_dict])
    # Reorder to the form-field order, then rename to model columns
    df = df[list(FEATURE_MAP.keys())]
    df.columns = [FEATURE_MAP[k] for k in FEATURE_MAP.keys()]
    # Now df.columns == ["Nitrogen","Phosphorus",...,"pH_Value","Rainfall"]
    return pipe.predict(df)[0]
