import logging
import os

def create_file_if_not_exists(relative_path):
    # Get the current working directory
    current_directory = os.getcwd()

    # Join the current directory with the relative path
    file_path = os.path.join(current_directory, relative_path)

    # Ensure the directory structure exists
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)

    if not os.path.exists(file_path):
        try:
            # Try to create the file
            with open(file_path, 'w'):
                print(f"File created at: {file_path}")
        except Exception as e:
            print(f"Error creating file: {e}")
    else:
        print(f"File already exists at: {file_path}")
    return file_path


def conf(file_path):
    create_file_if_not_exists(file_path)
    logging.basicConfig(filename=file_path, filemode='w', format='%(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)