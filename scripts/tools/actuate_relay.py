import sys

def main():
    if len(sys.argv) < 3:
        print("Usage: actuate_relay.py <pin_number> <state>")
        sys.exit(1)
        
    pin = sys.argv[1]
    state = sys.argv[2]
    
    # Aquí iría el código real interactuando con el hardware, por ej. sysfs gpio
    print(f"SUCCESS: Pin {pin} set to {state}")

if __name__ == "__main__":
    main()
