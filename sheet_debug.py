import google_auth_oauthlib.flow
import json
import os
import requests
from database import (
    create_table,
    insert_user,
    read_users,
    delete_user,
    find_user_by_email,
)
from google_sheets import (
    make_copy_of_sheet,
    authorize_client,
    get_sheets,
    get_sheet_data,
    update_existing_sheet,
    get_column_names,
    get_input_column_data,
    batch_update_sheet,
)
from tabulate import tabulate
from helper_functions import get_data_for_sheet_with_form

# sizing_sheet_name = "vuLogx"
# client, _ = authorize_client()
# spreadsheet_id = "1ntX-jpnNnfakFhjOdpyISky4IEfj4pA25NE9usUEewo"
# # First, ensure you have the correct column names
# data = get_sheet_data(client=client, spreadsheet_id=spreadsheet_id, sheet_number=1)
# # First, retrieve column names and print them to see if any are missing
# column_names = get_column_names(client=client, spreadsheet_id=spreadsheet_id, sheet_name=sizing_sheet_name)

# form_inputs = get_input_column_data(client=client, spreadsheet_id=spreadsheet_id, sheet_name= sizing_sheet_name, column_name=column_names[0])
# help_text = get_input_column_data(client=client, spreadsheet_id=spreadsheet_id, sheet_name= sizing_sheet_name, column_name=column_names[1])
# data_type = get_input_column_data(client=client, spreadsheet_id=spreadsheet_id, sheet_name= sizing_sheet_name, column_name=column_names[2])


# filtered_form_inputs = [item for item in form_inputs[2:] if item]
# filtered_help_text = [item for item in help_text[2:] if item]
# filtered_data_type = [item for item in data_type[2:] if item]

# # Combine the columns into a single list of rows
# table_data = list(zip(filtered_form_inputs, filtered_help_text, filtered_data_type))

# # Convert to a list of dictionaries
# json_data = [{"form_input": item[0], "help_text": item[1], "data_type": item[2]} for item in table_data]

# # Convert the list of dictionaries to JSON
# json_output = json.dumps(json_data, indent=4)

# # Print JSON output
# print(json_output)


# headers = ["S.No", "Form Input", "Help Text", "Data Type"]
# table_data_with_serial = [[i + 1] + list(row) for i, row in enumerate(table_data)]
# # Print the table
# #print(tabulate(table_data_with_serial, headers=headers, tablefmt="grid"))


# # Sheet Data ---------------------------------------------------------------->>>>>>>>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<--------------------------------------------------------------------

# # [['User Inputs', '', '', '', '', 'DERVIED INPUTS', '', '', '', ''],
# #   ['Form Input', 'Help Text', 'Type', 'Value(GB)', '', 'Data Size Per Event Assumed(bytes)', 'Total Rate at Kafka (EPS)', 'Total Event Rate at Storage(EPS)', 'Total Msg Rate at Kafka(kBps)', 'Size per Day on Storage(GB)'],
# #   ['Syslog Size per day(GB)', 'Approximate total size of parsed syslog metrics to be monitored per day', 'Numeric', '10', '', '500', '2236.5', '746', '1092', '7'],
# #   ['App Logs Size per day(GB)', 'Approximate total size of parsed application logs to be monitored per day', 'Numeric', '10', '', '1000', '559.5', '187', '546', '7'],
# #   ['Raw Logs storage', 'Should we need to store raw logs?', 'Boolean', 'FALSE', '', '1000', '0', '0', '0', '0'],
# #   ['', '', '', '', 'TOTAL', '', '2796', '933', '1638', '14']]


# vuLogx_file_path = "./form_inputs/vuLogx.json"

# # Load the JSON data from the file
# with open(vuLogx_file_path) as f:
#     vuLogx_data = json.load(f)

# # Print the data to verify it was loaded correctly
# print(vuLogx_data)


# def write_json_to_file(client, spreadsheet_id, sheet_name):
#     """Retrieve data from Google Sheet and write it to a JSON file."""
#     try:
#         print(f"Starting to retrieve data from the spreadsheet: {spreadsheet_id}, sheet: {sheet_name}")

#         # Ensure you have the correct column names
#         column_names = get_column_names(client=client, spreadsheet_id=spreadsheet_id, sheet_name=sheet_name)

#         form_inputs = get_input_column_data(client=client, spreadsheet_id=spreadsheet_id, sheet_name=sheet_name, column_name=column_names[0])
#         help_text = get_input_column_data(client=client, spreadsheet_id=spreadsheet_id, sheet_name=sheet_name, column_name=column_names[1])
#         data_type = get_input_column_data(client=client, spreadsheet_id=spreadsheet_id, sheet_name=sheet_name, column_name=column_names[2])

#         # Filter out empty items
#         filtered_form_inputs = [item for item in form_inputs[2:] if item]
#         filtered_help_text = [item for item in help_text[2:] if item]
#         filtered_data_type = [item for item in data_type[2:] if item]

#         # Combine the columns into a single list of rows
#         table_data = list(zip(filtered_form_inputs, filtered_help_text, filtered_data_type))

#         # Convert to a list of dictionaries
#         json_data = [{"form_input": item[0], "help_text": item[1], "data_type": item[2]} for item in table_data]

#         # Convert the list of dictionaries to JSON
#         json_output = json.dumps(json_data, indent=4)
#         print("JSON output created successfully.")

#         # Define the output file path based on the sheet name
#         output_file_path = f"./form_inputs/{sheet_name}.json"
#         print(f"Output file path: {output_file_path}")

#         # Write JSON output to the file, overwriting if it exists
#         with open(output_file_path, 'w') as json_file:
#             print(f"Writing JSON data to file: {output_file_path}")
#             json_file.write(json_output)

#         print(f"JSON data written to {output_file_path}")

#     except Exception as e:
#         print(f"Error writing JSON to file: {e}")


# # Example usage
# client, _ = authorize_client()  # Ensure you have a function to authorize your client
# spreadsheet_id = "1ntX-jpnNnfakFhjOdpyISky4IEfj4pA25NE9usUEewo"
# sizing_sheet_name = "vuBJM"

# write_json_to_file(client, spreadsheet_id, sizing_sheet_name)

gspread_client, drive_service, sheets_service = authorize_client()
# #  Get the form details from the JSON file
# with open("./form_inputs/form_inputs.json") as f:
#     form_data = json.load(f)
# data = []

# # # Input data for each of the sheets

# def prepare_data_for_sheets(sheet_name):
#     value_column = 'D'
#     length = len(form_data[sheet_name])
#     start_range = f"{value_column}3"
#     end_range = f"{value_column}{length + 3}"

#     sheet_data = {
#                 "range": f"{sheet_name}!{start_range}:{end_range}",
#                 "values": [[10]]
#     }
#     return sheet_data

# for sheet_name in form_data.keys():
#     data.append(prepare_data_for_sheets(sheet_name))

# print(data)


# # Update the user's copied spreadsheet


# print(batch_update_sheet(sheets_service, spreadsheet_id, sheets_data))


###########################**************************************************************************************************************************************

# def get_form_data_values(sheet_name, data):
#     """
#     Retrieve the values of formData for a given sheet_name.

#     Parameters:
#     - sheet_name (str): The key to look up in the data dictionary.
#     - data (dict): The dictionary containing form data.

#     Returns:
#     - list: A list of values from the formData for the specified sheet_name.
#     - None: If the sheet_name does not exist in the data.
#     """
#     # Check if the sheet_name exists in the data
#     if sheet_name in data:
#         # Extract formData and convert values as needed
#         return [
#             True if item['value'] == 'on' else
#             False if item['value'] == 'off' else
#             item['value']  # Keep numeric values as they are
#             for item in data[sheet_name]['formData']
#         ]
#     else:
#         # Return None if the sheet_name does not exist
#         return None

# # Example usage
# data = {
#     'vuLogx': {
#         'formData': [
#             {'name': 'vuLogx_Syslog Size per day(GB)', 'value': '21'},
#             {'name': 'vuLogx_App Logs Size per day(GB)', 'value': '21'},
#             {'name': 'vuLogx_Raw Logs storage', 'value': 'on'}  # Should return True
#         ]
#     },
#     'vuCoreML': {
#         'formData': [
#             {'name': 'vuCoreML_Num of Signals', 'value': '12'},
#             {'name': 'vuCoreML_Approx Num dimensions per signal', 'value': '21'},
#             {'name': 'vuCoreML_Num Fields Per Signal', 'value': '21'},
#             {'name': 'vuCoreML_LLM based Analytics', 'value': 'on'}  # Should return True
#         ]
#     }
# }

# # Call the function with 'vuLogx'
# values = get_form_data_values('vuCoreML', data)
# print(values)  # Output: ['21', '21', True]


# print(sheets_data)


data = {
    "vuLogx": {
        "formData": [
            {"name": "vuLogx_Syslog Size per day(GB)", "value": "100"},
            {"name": "vuLogx_App Logs Size per day(GB)", "value": "100"},
            {"name": "vuLogx_Raw Logs storage", "value": "off"},  # Should return True
        ]
    },
    "vuCoreML": {
        "formData": [
            {"name": "vuCoreML_Num of Signals", "value": "100"},
            {"name": "vuCoreML_Approx Num dimensions per signal", "value": "200"},
            {"name": "vuCoreML_Num Fields Per Signal", "value": "200"},
            {
                "name": "vuCoreML_LLM based Analytics",
                "value": "on",
            },  # Should return True
        ]
    },
}


print(get_data_for_sheet_with_form(data))
