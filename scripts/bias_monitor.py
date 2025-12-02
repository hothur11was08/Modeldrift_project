import os

# Ensure bias_reports folder exists
os.makedirs("bias_reports", exist_ok=True)

print("Running bias monitor...")

# Placeholder output
with open("bias_reports/bias.txt", "w") as f:
    f.write("Bias monitor placeholder: no bias detected.\n")

