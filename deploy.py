import argparse
import os
import subprocess
import sys

def run_command(command):
    """Runs a shell command and checks for errors."""
    print(f"Running: {command}")
    result = subprocess.run(command, shell=True, text=True)
    if result.returncode != 0:
        print(f"Error running command: {command}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Deploy and run meeting minutes automation on Slurm cluster.")
    parser.add_argument("input_file", help="Local path to the input audio/video file.")
    parser.add_argument("remote_host", help="Remote host (e.g., user@cc21dev0).")
    parser.add_argument("--remote_dir", default="Automation_minutes_Job", help="Remote directory to deploy to.")
    args = parser.parse_args()

    input_path = args.input_file
    remote_host = args.remote_host
    remote_dir = args.remote_dir
    
    if not os.path.exists(input_path):
        print(f"Error: Input file not found: {input_path}")
        sys.exit(1)

    input_filename = os.path.basename(input_path)
    
    print("=== Step 1: Archiving Project Code ===")
    # Exclude output, input (except the target file), .git, etc.
    # We'll just tar specific files/folders.
    archive_name = "project_code.tar.gz"
    run_command(f"tar -czf {archive_name} src/ main.py scripts/ pyproject.toml uv.lock README.md")

    print(f"\n=== Step 2: Transferring Files to {remote_host} ===")
    # Create remote directory
    run_command(f"ssh {remote_host} 'mkdir -p /work/$(whoami)/{remote_dir}/input /work/$(whoami)/{remote_dir}/logs'")
    
    # SCP Archive
    run_command(f"scp {archive_name} {remote_host}:/work/$(whoami)/{remote_dir}/")
    
    # SCP Input File
    print(f"Transferring {input_filename}...")
    run_command(f"scp {input_path} {remote_host}:/work/$(whoami)/{remote_dir}/input/")

    print("\n=== Step 3: Submitting Job ===")
    remote_script = f"""
    cd /work/$(whoami)/{remote_dir}
    tar -xzf {archive_name}
    # Submit job
    sbatch scripts/run_slurm.sh input/{input_filename}
    """
    
    run_command(f"ssh {remote_host} '{remote_script}'")

    print("\n=== Deployment Complete ===")
    print(f"Job submitted on {remote_host}.")
    print(f"Check logs in /work/$(whoami)/{remote_dir}/logs/")
    
    # Cleanup local archive
    os.remove(archive_name)

if __name__ == "__main__":
    main()
