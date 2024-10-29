import mwxml
import json

def save_json_to_file(json_data, file_path):
    """
    Saves the given JSON data to the specified file path.

    Args:
        json_data (dict or str): The JSON data to save, either as a dictionary or a JSON string.
        file_path (str): The path where the JSON data should be saved.
    """
    try:
        # Ensure the json_data is a string, if it's a dictionary convert it to a JSON string
        if isinstance(json_data, dict):
            json_data = json.dumps(json_data, ensure_ascii=False, indent=4)

        # Write the JSON string to the file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(json_data)
        
        print(f"JSON data successfully saved to {file_path}")
    except Exception as e:
        print(f"An error occurred while saving JSON data: {e}")

def get_page_content_as_json(dump_file_path, target_title) -> str:
    dump = mwxml.Dump.from_file(open(dump_file_path))
    for page in dump:
        if page.title == target_title:
            for revision in page:
                return revision.text
    return None

if __name__ == "__main__":
    # Usage example
    dump_file_path = "/home/gabortoth/Letöltések/huwiki-20241020-pages-articles.xml"
    target_title = "Szeged"
    page_content = get_page_content_as_json(dump_file_path, target_title)
    file_path = "/home/gabortoth/Letöltések/wikipedia_page.txt"

    # Print the returned JSON if it exists
    if page_content:
        save_json_to_file(page_content, file_path)
    else:
        print("Page not found.")

