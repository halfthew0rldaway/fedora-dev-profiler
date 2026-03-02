import os
import shutil

# Basic mapping of stack name to likely executable binaries indicating installation
STACK_BINARIES = {
    'Python': ['python3', 'pip', 'poetry'],
    'Node.js': ['node', 'npm', 'yarn', 'pnpm'],
    'Java': ['java', 'javac', 'mvn', 'gradle'],
    'Rust': ['rustc', 'cargo'],
    'Go': ['go'],
    'Docker/Podman': ['docker', 'dockerd', 'podman']
}

def detect_stacks() -> dict[str, dict]:
    """
    Detects which development stacks are installed on the system by checking binary paths.
    Returns a dictionary mapping stack name -> details
    """
    detected = {}
    for stack, binaries in STACK_BINARIES.items():
        found_bins = []
        for b in binaries:
            path = shutil.which(b)
            if path:
                found_bins.append({'binary': b, 'path': path})
        if found_bins:
            detected[stack] = {
                'installed': True,
                'binaries': found_bins
            }
    return detected
