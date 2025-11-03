# src/train_sarimax.py
from pathlib import Path
import pandas as pd, numpy as np, json, matplotlib.pyplot as plt
from statsmodels.tsa.statespace.sarimax import SARIMAX
from sklearn.metrics import mean_absolute_error, mean_squared_error

RAW = Path("data/raw"); REPORTS = Path("reports")
REPORTS.mkdir(exist_ok=True)

df = pd.read_csv(RAW/"cases.csv", parse_dates=["date"]).sort_values("date")

# hold out last 8 weeks
train = df.iloc[:-8].copy()
test  = df.iloc[-8:].copy()

model = SARIMAX(
    train["cases"],
    order=(1,1,1),
    seasonal_order=(1,0,1,52),  # yearly-ish pattern for weekly data
    enforce_stationarity=False,
    enforce_invertibility=False
)
fit = model.fit(disp=False)

pred = fit.get_forecast(steps=len(test))
pm = pred.predicted_mean
ci = pred.conf_int(alpha=0.05)

mae  = float(mean_absolute_error(test["cases"], pm))
rmse = float(np.sqrt(mean_squared_error(test["cases"], pm)))
with open(REPORTS/"metrics.json","w") as f: json.dump({"MAE":mae,"RMSE":rmse,"horizon_weeks":len(test)}, f, indent=2)

plt.figure()
plt.plot(train["date"], train["cases"], label="Train")
plt.plot(test["date"], test["cases"], label="Actual")
plt.plot(test["date"], pm, label="Forecast")
plt.fill_between(test["date"], ci.iloc[:,0], ci.iloc[:,1], alpha=0.2, label="95% CI")
plt.legend(); plt.title("US weekly SARS-CoV-2 wastewater (median percentile): SARIMAX forecast")
plt.tight_layout()
plt.savefig(REPORTS/"forecast.png", dpi=150)
