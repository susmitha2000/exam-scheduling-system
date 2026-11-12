
import hashlib
import subprocess
import sys
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parent
DATA_DIR = BACKEND_DIR.parent / "data"


def calculate_checksums():
    checksums = {}

    for file_path in sorted(DATA_DIR.iterdir()):
        if file_path.is_file() and file_path.suffix in (".csv", ".json"):
            file_hash = hashlib.sha256(file_path.read_bytes()).hexdigest()
            checksums[file_path.name] = file_hash

    return checksums


def run_generator():
    print("\nRunning synthetic data generator...")

    subprocess.run(
        [sys.executable, "generate_data.py"],
        cwd=BACKEND_DIR,
        check=True,
    )


def main():
    print("REPRODUCIBILITY VERIFICATION")
    print("============================")

    # First generation
    run_generator()
    first_checksums = calculate_checksums()

    # Second generation with the same fixed seed
    run_generator()
    second_checksums = calculate_checksums()

    if first_checksums == second_checksums:
        print("\nSUCCESS: Both generations produced identical files.")
        print(f"Files verified: {len(first_checksums)}")

        for filename, checksum in first_checksums.items():
            print(f"{filename}: {checksum}")

        print("\nREPRODUCIBILITY TEST PASSED")
    else:
        print("\nERROR: Generated files are different.")

        all_files = set(first_checksums) | set(second_checksums)

        for filename in sorted(all_files):
            if first_checksums.get(filename) != second_checksums.get(filename):
                print(f"Mismatch: {filename}")

        raise SystemExit(1)


if __name__ == "__main__":
    main()
