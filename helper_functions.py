import json


def load_and_collect_form_inputs(file_path):
    """Load JSON data from a specified file and collect form inputs into a dictionary."""
    try:
        with open(file_path, "r") as file:
            input_data = json.load(file)  # Load the JSON data
        print(f"Successfully loaded JSON data from {file_path}.")

        collected_data = {}  # Initialize a dictionary to hold collected data

        # Iterate through each sheet and its fields
        for sheet_name, fields in input_data.items():
            sheet_data = {}  # Initialize the dictionary for this sheet

            for field in fields:
                form_input = field["form_input"]
                sheet_data[form_input] = field["value"]  # Add form_input with its value

            collected_data[sheet_name] = (
                sheet_data  # Add the sheet data to the collected data
            )

        return collected_data  # Return the collected data

    except FileNotFoundError:
        print(f"Error: The file {file_path} does not exist.")
        return None  # Return None to indicate failure
    except json.JSONDecodeError:
        print(f"Error: The file {file_path} contains invalid JSON.")
        return None  # Return None to indicate failure
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None  # Return None to indicate failure


# # Uncomment the following code to test the function
# # Example usage
# file_path = './form_inputs/form_inputs.json'  # Replace with your JSON file path
# collected_data = load_and_collect_form_inputs(file_path)  # Load data and collect inputs

# # # Print the collected data if available
# # if collected_data:
# #     print(json.dumps(collected_data, indent=4))


def get_form_data_values(sheet_name, data):
    """
    Retrieve the values of formData for a given sheet_name.

    Parameters:
    - sheet_name (str): The key to look up in the data dictionary.
    - data (dict): The dictionary containing form data.

    Returns:
    - list: A list of values from the formData for the specified sheet_name.
    - None: If the sheet_name does not exist in the data.
    """
    # Check if the sheet_name exists in the data
    if sheet_name in data:
        # Ensure that formData is a list
        form_data_list = data[sheet_name].get("formData", [])
        # Extract formData and convert values as needed
        return [
            [
                (
                    True
                    if item["value"] == "TRUE"
                    else (
                        False
                        if item["value"] == "FALSE"
                        else (
                            int(item["value"])
                            if item["value"].isdigit()  # Convert string to int
                            else (
                                float(item["value"])
                                if item["value"]
                                .replace(".", "", 1)
                                .isdigit()  # Convert to float if it has a decimal
                                else item["value"]
                            )
                        )
                    )
                )  # Keep other values as they are
            ]
            for item in form_data_list
        ]
    else:
        # Return None if the sheet_name does not exist
        return None


def prepare_data_for_sheets(sheet_name, data):
    value_column = "D"
    length = len(data[sheet_name]["formData"])  # Use 'data' instead of 'form_data'
    start_range = f"{value_column}3"
    end_range = f"{value_column}{length + 3}"

    # Retrieve the form data values
    values = get_form_data_values(sheet_name, data)

    sheet_data = {
        "range": f"{sheet_name}!{start_range}:{end_range}",
        "values": (
            values if values is not None else [[]]
        ),  # Adjusted to provide a list of lists
    }
    return sheet_data


# Prepare sheet data for General Input and Data Retention because they are not in same format as other sheets

# General Input value cells are in the format of 'C3:C6' another thing is to care that the value of C4 is 0

# Data Retention value cells are in the format of 'B10:E10' , One more thing to care that default value of these cells are 10 ,
# so if the value is less than 10 then we need to update the value to 10

def prepare_general_input_data_for_sheets(data):
    general_input_data = get_form_data_values("GeneralInputs", data) or []
    data_retention_data = get_form_data_values("DataRetention", data) or []

    # Check if the data lists are empty; if so, return empty dictionaries
    if not general_input_data or not data_retention_data:
        return [], []

    # Make Data retention data in the format of 'B11:E11'
    data_retention_data = [item[0] for item in data_retention_data]

    # Update values less than 10 to be 10
    data_retention_data = [item if item >= 10 else 10 for item in data_retention_data]

    # Define ranges for Google Sheets API
    general_input_range = "General Inputs!C3:C6"
    data_retention_range = "General Inputs!B11:E11"

    # Prepare the dictionaries for Sheets API
    general_input_sheet_data = {
        "range": general_input_range,
        "values": general_input_data,
    }
    data_retention_sheet_data = {
        "range": data_retention_range,
        "values": [data_retention_data],  # Wrapping in a list to represent a row
    }

    return general_input_sheet_data, data_retention_sheet_data



# Prepare a list to hold the data for sheets

# Populate the sheets_data list with sheet data for each sheet name


def get_data_for_sheet_with_form(data):
    sheets_data = []
    # Need to ignore 2 sheets in the data dictionary
    # We will process them separately
    # 1. 'DataRetention'
    # 2. 'GeneralInputs'
    for sheet_name in data.keys():
        if sheet_name in ["DataRetention", "GeneralInputs"]:
            continue
        sheets_data.append(prepare_data_for_sheets(sheet_name, data=data))
        general_input_sheet_data, data_retention_sheet_data = prepare_general_input_data_for_sheets(data=data)
    sheets_data.append(general_input_sheet_data)
    sheets_data.append(data_retention_sheet_data)
    # Add the data for 'GeneralInputs' and 'DataRetention'
    return sheets_data


def map_form_values_db_template_values(form_data, template_data):
    # Ensure template_data is a dictionary
    if isinstance(template_data, str):
        template_data = json.loads(template_data)  # Parse JSON string to a dictionary

    # Ensure template_data is indeed a dictionary
    if not isinstance(template_data, dict):
        raise ValueError("template_data should be a dictionary.")

    # Iterate through the new structured form_data
    for section, section_data in form_data.items():
        if "formData" in section_data:
            for item in section_data["formData"]:
                # Each item has a 'name' and a 'value'
                component_name = item["name"]
                value = item["value"]

                # Split the component name to find the correct key
                key = component_name.split("_", 1)  # Split on the first underscore

                # Check if section exists in template_data and assign value
                if len(key) == 2:
                    sub_section, key_name = key
                    if sub_section in template_data and key_name in template_data[sub_section]:
                        template_data[sub_section][key_name] = value
                    else:
                        print(f"Component '{component_name}' not found in template data.")
                else:
                    print(f"Invalid component name format: '{component_name}'")

    return template_data

