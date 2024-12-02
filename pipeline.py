import subprocess
import os
import signal
import sys

def start_capture(output_file):
    """
    Start the Ubertooth to Wireshark pipeline to capture Bluetooth packets live and save the data.
    
    :param output_file: Path to save the captured data (e.g., 'capture.pcap').
    """
    try:
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_file), exist_ok=True)

        # Ubertooth command to capture BLE traffic
        ubertooth_cmd = ["ubertooth-btle", "-f", "-c", "-"]

        # Wireshark command to read from pipe and save data
        wireshark_cmd = [
            "wireshark",  # Replace with 'tshark' if live display isn't required
            "-k",  # Start capturing immediately
            "-i", "-",  # Read from standard input
            "-w", output_file  # Write capture to file
        ]

        print(f"Starting capture... Data will be displayed in Wireshark and saved to {output_file}")

        # Launch Ubertooth and pipe output to Wireshark
        with subprocess.Popen(ubertooth_cmd, stdout=subprocess.PIPE) as ubertooth_proc:
            with subprocess.Popen(wireshark_cmd, stdin=ubertooth_proc.stdout) as wireshark_proc:
                print("Press Ctrl+C to stop the capture.")
                wireshark_proc.wait()  # Wait for Wireshark to finish

    except KeyboardInterrupt:
        print("\nCapture stopped by user.")
    except FileNotFoundError as e:
        print(f"Error: {e}. Is 'ubertooth-btle' and 'wireshark' installed and in your PATH?")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        # Ensure any running processes are terminated
        try:
            if 'ubertooth_proc' in locals() and ubertooth_proc.poll() is None:
                ubertooth_proc.terminate()
            if 'wireshark_proc' in locals() and wireshark_proc.poll() is None:
                wireshark_proc.terminate()
        except Exception as cleanup_error:
            print(f"Error during cleanup: {cleanup_error}")

if __name__ == "__main__":
    # Output file for captured data
    output_file = "captures/bluetooth_traffic.pcap"

    # Ensure cleanup on script termination
    def signal_handler(sig, frame):
        print("\nTerminating processes...")
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    # Start the capture
    start_capture(output_file)
