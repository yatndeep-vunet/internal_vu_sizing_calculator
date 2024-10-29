import gspread
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.discovery import build
import json
import os
import dotenv
from tabulate import tabulate

dotenv.load_dotenv()
# Define the scope for Google Sheets API and Google Drive API
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
]

# Path to your downloaded JSON file
creds = ServiceAccountCredentials.from_json_keyfile_name(
    "./credentials/google_cred.json", scope
)


def authorize_client():
    """Authorize the Google Sheets and Drive API client."""
    client = gspread.authorize(creds)
    drive_service = build("drive", "v3", credentials=creds)
    # Authorize Google Sheets API client
    sheets_service = build("sheets", "v4", credentials=creds)

    return client, drive_service, sheets_service


def make_copy_of_sheet(drive_service, user_name):
    """Create a copy of the master spreadsheet for the user."""
    file_metadata = {
        "name": "Copy for " + user_name,
        "mimeType": "application/vnd.google-apps.spreadsheet",
    }
    master_spreadsheet_id = os.getenv("MASTER_SPREADSHEET_ID")

    # Copy the master sheet
    file_copy = (
        drive_service.files()
        .copy(fileId=master_spreadsheet_id, body=file_metadata)
        .execute()
    )
    return file_copy["id"]


def update_existing_sheet(client, spreadsheet_id, range_name, values, sheet_number):
    """Update the user's copied spreadsheet."""
    try:
        spreadsheet = client.open_by_key(spreadsheet_id)
        worksheet = spreadsheet.get_worksheet(
            sheet_number
        )  # Access the sheet with the number
        worksheet.update(range_name, values)
    except Exception as e:
        print(f"Error updating sheets: {e}")
        return None


def get_sheets(client, spreadsheet_id):
    """Retrieve all sheets in the specified spreadsheet."""
    try:
        spreadsheet = client.open_by_key(spreadsheet_id)  # Open the spreadsheet by ID
        worksheets = spreadsheet.worksheets()  # Get all worksheets
        sheet_names = [
            worksheet.title for worksheet in worksheets
        ]  # Extract the titles
        return sheet_names
    except Exception as e:
        print(f"Error retrieving sheets: {e}")
        return None


def get_sheet_data(client, spreadsheet_id, sheet_number):
    """Retrieve data from a specific sheet by its name."""
    try:
        spreadsheet = client.open_by_key(spreadsheet_id)  # Open the spreadsheet by ID
        worksheet = spreadsheet.get_worksheet(sheet_number)  # Get the worksheet by name
        data = worksheet.get_all_values()  # Fetch all data as a list of dictionaries
        return data
    except Exception as e:
        print(f"Error retrieving data from sheet '{sheet_number}': {e}")
        return None


def get_sheet_data_with_sheet_name(client, spreadsheet_id, sheet_name):
    """Retrieve data from a specific sheet by its name."""
    try:
        spreadsheet = client.open_by_key(spreadsheet_id)  # Open the spreadsheet by ID
        worksheet = spreadsheet.worksheet(sheet_name)  # Get the worksheet by name
        data = worksheet.get_all_values()  # Fetch all data as a list of dictionaries
        return data
    except Exception as e:
        print(f"Error retrieving data from sheet '{sheet_name}': {e}")
        return None


def get_column_names(client, spreadsheet_id, sheet_name):
    """Retrieve column names from the specified sheet."""
    try:
        # Open the spreadsheet and the specified sheet
        spreadsheet = client.open_by_key(spreadsheet_id)
        worksheet = spreadsheet.worksheet(sheet_name)  # Get the worksheet by name

        # Get all values in the sheet
        all_values = worksheet.get_all_values()  # Returns a list of lists

        if not all_values:
            print("The sheet is empty.")
            return []

        # Assume first row contains headers (column names)
        column_names = all_values[1]  # Get the first row

        return column_names

    except Exception as e:
        print(f"Error retrieving column names: {e}")
        return []


def get_input_column_data(client, spreadsheet_id, sheet_name, column_name):
    """Retrieve data from a specific column in a sheet by column name."""
    try:
        # Open the spreadsheet and the specific sheet
        spreadsheet = client.open_by_key(spreadsheet_id)
        worksheet = spreadsheet.worksheet(sheet_name)  # Get the worksheet by name

        # Get all values in the sheet
        all_values = worksheet.get_all_values()  # Returns a list of lists

        if not all_values:
            print("The sheet is empty.")
            return None

        # Extract column names from the first row
        # We will ignore the first  row as it is User Input or Derived Input
        headers = all_values[1]  # Assume first row contains headers

        # Find the index of the specified column name
        if column_name not in headers:
            print(f"Column '{column_name}' does not exist in the sheet.")
            return None

        column_index = headers.index(column_name)  # Get the index of the column

        # Retrieve all values from the specified column
        column_data = [row[column_index] for row in all_values]  # Skip header row

        return column_data

    except Exception as e:
        print(f"Error retrieving column data: {e}")
        return None


def get_form_details(client, spreadsheet_id, product_sheet_name):
    """Retrieve form details from the Google Sheet, with error handling."""
    try:
        # Authorize client
        client, _ = authorize_client()
    except Exception as e:
        print(f"Error authorizing client: {e}")
        return None

    try:
        # Retrieve column names
        column_names = get_column_names(
            client=client, spreadsheet_id=spreadsheet_id, sheet_name=product_sheet_name
        )
        if not column_names or len(column_names) < 3:
            raise ValueError(
                "Insufficient column names or missing columns in the sheet."
            )
    except Exception as e:
        print(f"Error retrieving column names: {e}")
        return None

    try:
        # Retrieve columns based on column names
        form_inputs = get_input_column_data(
            client=client,
            spreadsheet_id=spreadsheet_id,
            sheet_name=product_sheet_name,
            column_name=column_names[0],
        )
        help_text = get_input_column_data(
            client=client,
            spreadsheet_id=spreadsheet_id,
            sheet_name=product_sheet_name,
            column_name=column_names[1],
        )
        data_type = get_input_column_data(
            client=client,
            spreadsheet_id=spreadsheet_id,
            sheet_name=product_sheet_name,
            column_name=column_names[2],
        )

        # Ensure data retrieval was successful
        if not form_inputs or not help_text or not data_type:
            raise ValueError("One or more columns could not be retrieved.")
    except Exception as e:
        print(f"Error retrieving data from columns: {e}")
        return None

    try:
        # Filter out empty items in each list (skip header and empty rows)
        filtered_form_inputs = [item for item in form_inputs[2:] if item]
        filtered_help_text = [item for item in help_text[2:] if item]
        filtered_data_type = [item for item in data_type[2:] if item]

        # Ensure all columns have the same length
        if not (
            len(filtered_form_inputs)
            == len(filtered_help_text)
            == len(filtered_data_type)
        ):
            raise ValueError("Column lengths do not match. Data may be incomplete.")

        # Combine columns into a list of rows
        table_data = list(
            zip(filtered_form_inputs, filtered_help_text, filtered_data_type)
        )

        # Convert to a list of dictionaries
        json_data = [
            {"form_input": item[0], "help_text": item[1], "data_type": item[2]}
            for item in table_data
        ]

        # Convert to JSON string
        json_output = json.dumps(json_data, indent=4)
    except Exception as e:
        print(f"Error processing data into JSON format: {e}")
        return None

    return json_output


def batch_update_sheet(service, spreadsheet_id, data):
    """
    Perform a batch update on a Google Spreadsheet.

    Parameters:
    - service: Authorized Google Sheets API client.
    - spreadsheet_id: The ID of the spreadsheet to update.
    - data: A list of dictionaries, each containing:
        - 'range': The cell range to update (e.g., 'Sheet1!A1:B2').
        - 'values': The data to place within the specified range.

    Returns:
    - The total number of cells updated.
    """
    # Prepare the request body for batch update
    body = {
        "valueInputOption": "RAW",  # Use 'USER_ENTERED' if Google Sheets should interpret values
        "data": data,
    }

    try:
        # Execute the batch update
        result = (
            service.spreadsheets()
            .values()
            .batchUpdate(spreadsheetId=spreadsheet_id, body=body)
            .execute()
        )

        print(f"{result.get('totalUpdatedCells')} cells updated.")
        return result.get("totalUpdatedCells")
    except Exception as e:
        print(f"Error updating sheet: {e}")
        return None

def list_spreadsheets(drive_service):
            """
            List all spreadsheets accessible by the service account.

            Parameters:
            - drive_service: Authorized Google Drive API client.

            Returns:
            - A list of dictionaries, each containing:
                - 'name': The name of the spreadsheet.
                - 'id': The ID of the spreadsheet.
            """
            try:
                # Query to list only Google Sheets files
                query = "mimeType='application/vnd.google-apps.spreadsheet'"
                results = drive_service.files().list(q=query).execute()
                items = results.get('files', [])

                spreadsheets = [{'name': item['name'], 'id': item['id']} for item in items]

                return spreadsheets
            except Exception as e:
                print(f"Error listing spreadsheets: {e}")
                return []

# client, drive_service, sheets_service = authorize_client()

# # List all spreadsheets
# spreadsheets = list_spreadsheets(drive_service)

# # Prepare data for tabulation
# table_data = [[index + 1, sheet['name'], sheet['id']] for index, sheet in enumerate(spreadsheets)]

# # Print the table
# print(tabulate(table_data, headers=["S. No.", "Spreadsheet Name", "Spreadsheet ID"], tablefmt="grid"))

# def delete_spreadsheets(drive_service, spreadsheet_ids):
#     """Delete multiple spreadsheets by their IDs."""
#     for spreadsheet_id in spreadsheet_ids:
#         try:
#             drive_service.files().delete(fileId=spreadsheet_id).execute()
#             print(f"Spreadsheet with ID {spreadsheet_id} deleted successfully.")
#         except Exception as e:
#             print(f"Error deleting spreadsheet with ID {spreadsheet_id}: {e}")
#             continue


# delete_spreadsheets(drive_service, spreadsheet_ids_to_delete)
