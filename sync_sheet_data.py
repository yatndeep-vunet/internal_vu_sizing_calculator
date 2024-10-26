from google_sheets import authorize_client, get_column_names, get_input_column_data
import json
import os


def write_json_to_file(client, spreadsheet_id, sheet_names):
    """Retrieve data from Google Sheets and write it to a single JSON file, preserving existing data."""
    try:
        print(f"Starting to retrieve data from the spreadsheet: {spreadsheet_id}")

        # Initialize the all_data dictionary
        all_data = {}

        # Define the output file path
        output_file_path = "./form_inputs/form_inputs.json"

        # Check if the JSON file exists and read existing data
        if os.path.exists(output_file_path):
            with open(output_file_path, "r") as json_file:
                all_data = json.load(json_file)
                print(f"Loaded existing data from {output_file_path}.")

        for sheet_name in sheet_names:
            print(f"Retrieving data for sheet: {sheet_name}")

            # Ensure you have the correct column names
            column_names = get_column_names(
                client=client, spreadsheet_id=spreadsheet_id, sheet_name=sheet_name
            )

            form_inputs = get_input_column_data(
                client=client,
                spreadsheet_id=spreadsheet_id,
                sheet_name=sheet_name,
                column_name=column_names[0],
            )
            help_text = get_input_column_data(
                client=client,
                spreadsheet_id=spreadsheet_id,
                sheet_name=sheet_name,
                column_name=column_names[1],
            )
            data_type = get_input_column_data(
                client=client,
                spreadsheet_id=spreadsheet_id,
                sheet_name=sheet_name,
                column_name=column_names[2],
            )
            value = get_input_column_data(
                client=client,
                spreadsheet_id=spreadsheet_id,
                sheet_name=sheet_name,
                column_name=column_names[3],
            )

            # Filter out empty items
            filtered_form_inputs = [item for item in form_inputs[2:] if item]
            filtered_help_text = [item for item in help_text[2:] if item]
            filtered_data_type = [item for item in data_type[2:] if item]
            filtered_value = [
                float(item) if item not in ["TRUE", "FALSE"] and item.strip() else item 
                for item in value[2:]
            ]


            # Combine the columns into a single list of rows
            table_data = list(
                zip(filtered_form_inputs, filtered_help_text, filtered_data_type , filtered_value)
            )

            # Convert to a list of dictionaries
            json_data = [
                {"form_input": item[0], "help_text": item[1], "data_type": item[2], "value": item[3]}
                for item in table_data
            ]

            # Add or update the data for the current sheet in all_data
            all_data[sheet_name] = json_data
            print(f"Data retrieved for sheet {sheet_name}: {len(json_data)} entries")
        # Convert the complete dictionary to JSON
        json_output = json.dumps(all_data, indent=4)
        print("Combined JSON output created successfully.")

        # Write JSON output to the file, overwriting if it exists
        with open(output_file_path, "w") as json_file:
            print(f"Writing JSON data to file: {output_file_path}")
            json_file.write(json_output)

        print(f"JSON data written to {output_file_path}")

    except Exception as e:
        print(f"Error writing JSON to file: {e}")


# Example usage
client, _, _ = authorize_client()  # Ensure you have a function to authorize your client


# sizing_sheet_names = ["vuBJM", "vuLogx"]
# write_json_to_file(client, spreadsheet_id, sizing_sheet_names)
