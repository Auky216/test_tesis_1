import sys

def main():
    if len(sys.argv) < 3:
        print("Usage: log_anomaly.py <sensor_name> <reason>")
        sys.exit(1)
        
    sensor = sys.argv[1]
    reason = sys.argv[2]
    
    print(f"ANOMALY LOGGED: Sensor {sensor} - Reason: {reason}")

if __name__ == "__main__":
    main()
