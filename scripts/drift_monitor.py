import os
import matplotlib.pyplot as plt

# Ensure drift_reports folder exists
os.makedirs("drift_reports", exist_ok=True)

print("Running drift detection...")

# Example drift detection placeholder plot
plt.figure()
plt.plot([0, 1, 2], [0, 1, 0], label="dummy drift")
plt.title("Drift Detection Example")
plt.legend()

# Save into drift_reports folder
plt.savefig("drift_reports/drift.png", dpi=150, bbox_inches="tight")

