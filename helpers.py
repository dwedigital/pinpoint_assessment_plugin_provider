import base64


def svg_to_base64(svg_string):
    """
    Convert SVG string to base64 encoded string

    Args:
        svg_string (str): The SVG content as a string

    Returns:
        str: Base64 encoded SVG with data URI prefix
    """
    # Encode the SVG string to bytes
    svg_bytes = svg_string.encode("utf-8")

    # Encode to base64
    base64_svg = base64.b64encode(svg_bytes).decode("utf-8")

    # Return with data URI prefix
    return f"data:image/svg+xml;base64,{base64_svg}"


def svg_file_to_base64(svg_file_path):
    """
    Convert SVG file to base64 encoded string

    Args:
        svg_file_path (str): Path to the SVG file

    Returns:
        str: Base64 encoded SVG with data URI prefix
    """
    try:
        # Read the SVG file
        with open(svg_file_path, "rb") as file:
            # Read binary data
            svg_data = file.read()

            # Encode to base64
            base64_svg = base64.b64encode(svg_data).decode("utf-8")

            # Return with data URI prefix
            return f"data:image/svg+xml;base64,{base64_svg}"
    except FileNotFoundError:
        return "Error: File not found"
    except Exception as e:
        return f"Error: {str(e)}"


def png_to_base64(png_file_path):
    """
    Convert PNG file to base64 encoded string

    Args:
        png_file_path (str): Path to the PNG file

    Returns:
        str: Base64 encoded PNG with data URI prefix
    """
    try:
        # Read the PNG file in binary mode
        with open(png_file_path, "rb") as image_file:
            # Read the binary data
            binary_data = image_file.read()

            # Encode to base64
            base64_data = base64.b64encode(binary_data).decode("utf-8")

            # Return with data URI prefix
            return f"data:image/png;base64,{base64_data}"
    except FileNotFoundError:
        return "Error: File not found"
    except Exception as e:
        return f"Error: {str(e)}"


def jpg_to_base64(jpg_file_path):
    """
    Convert JPG/JPEG file to base64 encoded string

    Args:
        jpg_file_path (str): Path to the JPG/JPEG file

    Returns:
        str: Base64 encoded JPG with data URI prefix
    """
    try:
        # Read the JPG file in binary mode
        with open(jpg_file_path, "rb") as image_file:
            # Read the binary data
            binary_data = image_file.read()

            # Encode to base64
            base64_data = base64.b64encode(binary_data).decode("utf-8")

            # Return with data URI prefix
            return f"data:image/jpeg;base64,{base64_data}"
    except FileNotFoundError:
        return "Error: File not found"
    except Exception as e:
        return f"Error: {str(e)}"


def get_field_value(data, field_key):
    for field in data["formFields"]:
        if field["key"] == field_key:
            return field["value"]
    return None

def get_configuration_value(data, field_key):
    for config in data.get("configurationValues", []):
        if config["key"] == field_key:
            return config["value"]
    return None


def get_assessment_database():
    import json

    try:
        with open("assessments_database.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        return []
    except Exception as e:
        print(f"Error reading assessments database: {str(e)}")
        return []
    
def write_assessments_database(assessments):
    import json

    try:
        with open("assessments_database.json", "w") as file:
            json.dump(assessments, file, indent=4)
            return True
    except Exception as e:
        print(f"Error writing assessments database: {str(e)}")
        return False
