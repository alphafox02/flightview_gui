import subprocess
import time

def run_process():
    while True:
        try:
            # Run the main process
            subprocess.run(["python", "adsb-data-collector.py"])
        except Exception as e:
            print(f"Error: {e}")
            pass

        # Restart after a delay if the process ends
        time.sleep(10)

if __name__ == "__main__":
    run_process()
