import os
import subprocess
import sys
import logging

def print_header(title):
    print("\n" + "=" * 50)
    print(f"🚀 {title}")
    print("=" * 50 + "\n")

def print_section(title):
    print(f"\n📋 {title}:")

def print_success(message):
    print(f"✅ {message}")

def print_error(message):
    print(f"❌ {message}")

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

def run_command(command):
    print(f"⚙️  Executing: {command}")
    try:
        result = subprocess.run(command, shell=True, text=True, capture_output=True, check=True)
        if result.stdout:
            logger.info(f"Command output:\n{result.stdout.strip()}")
        if result.stderr:
            logger.warning(f"Command stderr:\n{result.stderr.strip()}")
        print_success("Command executed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"Command failed: {e}")
        logger.error(f"Error output:\n{e.stderr}")
        sys.exit(1)


def get_extension(format):
    return {"zip": ".zip", "tar": ".tar", "tgz": ".tgz", "tbz2": ".tbz2"}.get(
        format, ""
    )


def adjust_path(path):
    adjusted_path = (
        path
        if os.path.isabs(path)
        else os.path.join(os.getenv("GITHUB_WORKSPACE", os.getcwd()), path)
    )
    print(f"Adjusted path: {adjusted_path}")
    return adjusted_path


def compress(source, format, include_root):
    print_header("Compression Process Started")
    
    if not os.path.exists(source):
        print_error(f"Source path '{source}' does not exist")
        sys.exit(1)
    
    source = adjust_path(source)
    print_section("Configuration")
    print(f"  • Source: {source}")
    print(f"  • Format: {format}")
    print(f"  • Include Root: {include_root}")
    
    cwd = os.getcwd()
    print(f"  • Initial Directory: {cwd}")

    dest = os.getenv("DEST", os.getenv("GITHUB_WORKSPACE", os.getcwd()))
    if dest and not os.path.exists(dest):
        os.makedirs(dest)

    base_name = os.path.basename(source)
    extension = get_extension(format)
    full_dest = os.path.join(dest, f"{base_name}{extension}")
    print(f"Destination Path: {full_dest}")  # Debug: Show full destination path

    if os.path.isdir(source):
        # Compress a directory with the option of including root
        print(f"Attempting to compress directory {source} to {full_dest}")
        if include_root == "true":
            compress_target = base_name
            os.chdir(os.path.dirname(source))  # Change to directory of the source
        else:
            compress_target = "."
            os.chdir(
                source
            )  # Change to the source directory itself to compress its contents
        print(
            f"Changed CWD for Compression: {os.getcwd()}"
        )  # Debug: Show CWD for compression
    else:
        # Compress a file - include_root has no effect here
        print(f"Attempting to compress file {source} to {full_dest}")
        compress_target = base_name
        # os.chdir(os.path.dirname(source))  # Change to directory of the source

    if format == "zip":
        run_command(f"zip -r {full_dest} {compress_target}")
    elif format == "tar":
        run_command(f"tar --absolute-names -cvf {full_dest} {compress_target}")
    elif format == "tgz":
        run_command(f"tar -P -czvf {full_dest} {compress_target}")
    elif format == "tbz2":
        run_command(f"tar -P -cjvf {full_dest} {compress_target}")
    else:
        sys.exit(f"Unsupported format: {format}")
    os.chdir(cwd)  # Restore original working directory.
    print(f"Restored CWD: {os.getcwd()}")  # Debug: Show restored working directory
    print_success(f"Compression completed: {full_dest}")
    print("\n" + "=" * 50)
    print(
        f"file_path={full_dest}",
        file=open(os.getenv("GITHUB_OUTPUT", "/dev/stdout"), "a"),
    )


def decompress(source, format):
    print_header("Decompression Process Started")
    
    if not os.path.exists(source):
        print_error(f"Source file '{source}' does not exist")
        sys.exit(1)
    
    source = adjust_path(source)
    print_section("Configuration")
    print(f"  • Source: {source}")
    print(f"  • Format: {format}")
    print(f"  • Destination: {os.getenv('DEST', 'current directory')}")

    dest = os.getenv("DEST", os.getenv("GITHUB_WORKSPACE", os.getcwd()))
    if dest and not os.path.exists(dest):
        os.makedirs(dest)

    print(
        f"Attempting to decompress {source} to {dest if dest else 'current directory'}"
    )

    if format == "zip":
        unzip_options = f"-d {dest}" if dest else "-j -d ."
        run_command(f"unzip {unzip_options} {source}")
    elif format == "tar":
        tar_options = f"-C {dest}" if dest else "-C ."
        run_command(f"tar --absolute-names -xvf {source} {tar_options}")
    elif format == "tgz":
        tar_options = f"-C {dest}" if dest else "-C ."
        run_command(f"tar -P -xzvf {source} {tar_options}")
    elif format == "tbz2":
        tar_options = f"-C {dest}" if dest else "-C ."
        run_command(f"tar -P -xjvf {source} {tar_options}")
    else:
        sys.exit(f"Unsupported format: {format}")
    print_success("Decompression completed successfully")
    print("\n" + "=" * 50)
    print(
        f"file_path={dest if dest else 'current directory'}",
        file=open(os.getenv("GITHUB_OUTPUT", "/dev/stdout"), "a"),
    )


if __name__ == "__main__":
    command = os.getenv("COMMAND")
    source = os.getenv("SOURCE")
    format = os.getenv("FORMAT")
    include_root = os.getenv("INCLUDEROOT", "true")

    print_header("Compress/Decompress Action")
    print_section("Environment Configuration")
    print(f"  • Command: {command}")
    print(f"  • Source: {source}")
    print(f"  • Format: {format}")
    print(f"  • Include Root: {include_root}")
    
    if command == "compress":
        compress(source, format, include_root)
    elif command == "decompress":
        decompress(source, format)
    else:
        print_error(f"Invalid command: {command}")
        sys.exit(1)
