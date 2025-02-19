import os

# Get the absolute path of the 'training' directory
script_dir = os.path.dirname(os.path.abspath(__file__))
training_dir = os.path.dirname(script_dir)

# Path to the 'data' directory
data_dir = os.path.join(training_dir, "data")


def list_subdirectories(directory):
    """Lists subdirectories in the given directory."""
    if not os.path.exists(directory):
        print(f"Directory '{directory}' not found.")
        return []

    subdirs = [
        d for d in os.listdir(directory) if os.path.isdir(os.path.join(directory, d))
    ]

    if not subdirs:
        print(f"No folders found in '{directory}'.")
    return subdirs


if __name__ == "__main__":
    subdirectories = list_subdirectories(data_dir)
    print("Subdirectories in 'data':", subdirectories)
