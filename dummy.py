import subprocess

# Run the dir command
result = subprocess.run(['dir'], capture_output=True, text=True)

# Print the output
print(result.stdout)
