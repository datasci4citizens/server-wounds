import pandas as pd

# Load the CSV file
csv_path = 'infection_ischemia_model/labels.csv'
df = pd.read_csv(csv_path)

# Add .jpg to the end of each filename (after stripping whitespace)
df['filename'] = df['filename'].astype(str).str.strip() + '.jpg'

# Save the modified DataFrame back to CSV (overwrite)
df.to_csv(csv_path, index=False)

print("Updated 'filename' column and saved to CSV.")