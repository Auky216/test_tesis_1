import sys
import subprocess

if len(sys.argv) < 2:
    print("Error: Missing bash command argument.")
    sys.exit(1)

command = " ".join(sys.argv[1:])

try:
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    out = result.stdout.strip()
    err = result.stderr.strip()
    
    if result.returncode == 0:
        if out:
            print(f"Success:\n{out}")
        else:
            print("Success. (No output)")
    else:
        print(f"Failed with exit code {result.returncode}:\n{err}")
except Exception as e:
    print(f"Execution Error: {e}")
