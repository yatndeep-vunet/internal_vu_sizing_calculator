from flask import (
    Flask,
    redirect,
    session,
    url_for,
    request,
    render_template,
    flash,
    Response,
    jsonify,
)
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
    update_template_data,
    update_spreadsheet_id,
    find_user_template_data,
    update_template_data_by_frontend
)
from google_sheets import (
    make_copy_of_sheet,
    authorize_client,
    get_sheets,
    get_sheet_data,
    update_existing_sheet,
    get_form_details,
    batch_update_sheet,
    get_sheet_data_with_sheet_name,
    delete_spreadsheets,
    batch_get_sheet_data
)
from tabulate import tabulate
from helper_functions import load_and_collect_form_inputs, get_data_for_sheet_with_form , map_form_values_db_template_values

form_inputs = "./form_inputs/form_inputs.json"
from dotenv import load_dotenv
import time
from threading import Lock

app = Flask(__name__ ,static_folder='static',static_url_path='/internal/static')
app.secret_key = os.environ.get("FLASK_SECRET_KEY") or os.urandom(24)

# Load OAuth configuration
try:
    with open("./credentials/client_secret.json") as f:
        oauth_config = json.load(f)
except FileNotFoundError:
    print("Error: client_secret.json file not found.")
    oauth_config = None

oauth_flow = (
    google_auth_oauthlib.flow.Flow.from_client_config(
        oauth_config,
        scopes=[
            "https://www.googleapis.com/auth/userinfo.email",
            "openid",
            "https://www.googleapis.com/auth/userinfo.profile",
        ],
    )
    if oauth_config
    else None
)


@app.route("/internal/signin")
def signin():
    if not oauth_flow:
        return "OAuth configuration is missing. Cannot initiate signin.", 500

    oauth_flow.redirect_uri = url_for("oauth2callback", _external=True).replace(
        "http://", "http://"
    )
    authorization_url, state = oauth_flow.authorization_url()
    session["state"] = state
    return redirect(authorization_url)


@app.route("/internal/callback")
def oauth2callback():
    if not session.get("state") or session["state"] != request.args.get("state"):
        return "Invalid state parameter", 400

    try:
        oauth_flow.fetch_token(
            authorization_response=request.url.replace("http:", "https:")
        )
        session["access_token"] = oauth_flow.credentials.token

        user_info = get_user_info(session["access_token"])
        if user_info and "email" in user_info and "given_name" in user_info:
            existing_users = read_users()
            user_exists = any(user[2] == user_info["email"] for user in existing_users)

            if not user_exists:
                insert_user(
                    user_info["given_name"], user_info["email"], "Null", "Null", "Null"
                )
            return redirect(url_for("welcome"))
        else:
            print("User info retrieval failed or incomplete data.")
            return "User info could not be fetched.", 400
    except Exception as e:
        print(f"OAuth2 callback error: {e}")
        return "Authentication failed. Please try again.", 500


def login_required(f):
    """Decorator to require login for specific routes."""

    def wrap(*args, **kwargs):
        if "access_token" in session:
            return f(*args, **kwargs)
        else:
            flash("You must be logged in to access this page.")
            return redirect(
                url_for("welcome")
            )  # Change to redirect to the sign-in page

    wrap.__name__ = f.__name__
    return wrap


@app.route("/internal/home")
def welcome():
    try:
        # Check if the access token is in the session
        if "access_token" in session:
            user_personal_info = get_user_info(session["access_token"])
            # Ensure user_personal_info is valid
            if user_personal_info is not None:
                detail_user_info = find_user_by_email(email=user_personal_info["email"])
                # Initialize spreadsheet_data
                template_data = []

                # Get the user's spreadsheet data if it exists
            if detail_user_info[5]:
                if detail_user_info[5] != "Null":
                    try:
                        template_data = json.loads(detail_user_info[5])
                    except json.JSONDecodeError as e:
                        print(f"JSON decoding error: {e}")  # Log error
                        template_data = {}  # Default to an empty dict
                else:
                    template_data = {}  # Handle case where value is "Null"
            else:
                template_data = {}  # Handle case where the value is empty or None

            page_info = {
                "title": "vuSizing Calculator",
                "description": "Welcome to the application.",
                "user_info": {
                    "user_personal_info": user_personal_info,
                    "user_assets": template_data,
                },
                "data": {},
            }

            return render_template("welcome.html", page_info=page_info)

        # If access token is not present or user info is invalid, render with None
        page_info = {
                "title": "vuSizing Calculator",
                "description": "Welcome to the application.",
            }
        return render_template("welcome.html", page_info=page_info)

    except Exception as e:
        print(f"Welcome page error: {e}")
        return "An error occurred while loading the page. Please try again later.", 500


@app.route("/internal/create_template", methods=["POST"])
@login_required
def create_template():
    try:
        user_personal_info = get_user_info(session["access_token"])
        detail_user_info = find_user_by_email(email=user_personal_info["email"])

        try:
            json_string = detail_user_info[5]
            if json_string:
                existing_template_data = json.loads(json_string)
            else:
                existing_template_data = []
        except json.JSONDecodeError:
            print("Failed to decode JSON. Ensure JSON format is correct.")
            existing_template_data = []

        # Get template name from form
        template_name = request.form.get("template_name")
        spreadsheet_name = f"sheet_for_{user_personal_info['name']}"

        # Check if template_name is unique
        if any(
            item["template_name"] == template_name for item in existing_template_data
        ):
            flash("Template name must be unique. Please choose a different name.")
            return redirect(url_for("welcome"))

        # Create a copy of the template sheet

        if detail_user_info[3] == "Null":
            drive_service = authorize_client()[1]
            spreadsheet_id = make_copy_of_sheet(
                drive_service, user_personal_info["email"]
            )
            
            update_spreadsheet_id(
                email=user_personal_info["email"],
                spreadsheet_id=spreadsheet_id,
                spreadsheet_name=spreadsheet_name,
            )
        else:
            spreadsheet_id = detail_user_info[2]
        
        default_form_status ={
                'vuLogx': False, 
                'vuBJM': False, 
                'vuInfra': False, 
                'vuTraces': False,
                'vuCoreML': False, 
                'DataRetention': True, 
                'GeneralInputs': True
                }

        new_template_data = {
                "template_name": template_name,
                "template_data":{
                    "form_status" : default_form_status,
                    "form_data" : load_and_collect_form_inputs(form_inputs)
                }   
            }
        
        # Append new data to existing spreadsheet data
        updated_template_data = existing_template_data + [new_template_data]

        # Update the database with the combined data
        update_result = update_template_data(
            email=user_personal_info["email"], template_data=updated_template_data
        )
        if update_result != "Template updated successfully.":
            flash("Failed to update template data. Please try again.")
            return redirect(url_for("welcome"))
        else:
            flash("Template created successfully.")

        return redirect(url_for("welcome"))
    except Exception as e:
        print(f"Create template error: {e}")
        flash("Failed to create template. Please try again.")
        return redirect(url_for("welcome"))


# Getting the template name from the URL


@app.route("/internal/template/<template_name>")
@login_required
def template(template_name):
    try:
        user_personal_info = get_user_info(session["access_token"])
        # detail_user_info = find_user_by_email(email=user_personal_info["email"])

        # Get the form details from the JSON file
        with open(form_inputs) as f:
            form_data = json.load(f)

        page_info = {
            "title": f"vuSizing Calc - {template_name}",
            "description": "Template page",
            "user_info": {
                "user_personal_info": user_personal_info,
                "template_name": template_name,
            },
            "data": form_data,
            "table_data": None
        }
        return render_template("template.html", page_info=page_info)
    except Exception as e:
        print(f"Template page error: {e}")
        return (
            "An error occurred while fetching the template. Please try again later.",
            500,
        )

@app.route("/internal/calculate", methods=["POST"])
def calculate_result():
    try:
        user_personal_info = get_user_info(session["access_token"])
        detail_user_info = find_user_by_email(email=user_personal_info["email"])
        spreadsheet_id = detail_user_info[3]
        data = request.get_json()  # Parse JSON data
        form_status = data.get('form_status')
        form_data = data.get('form_data')
        gspread_client, drive_service, sheets_service = authorize_client()     
        if form_data is None:
            return jsonify({"message": "No data received."}), 400
        # print("Form Data from frontend:", form_data)  # Process form_data as needed
        print("Data is under processing ..............................................")
        # Actually what happens here is that we are getting the data from the frontend and then we are processing it
        # Process it to make it ready to be sent to the sheets
        processed_data_for_sheets = get_data_for_sheet_with_form(form_data)
        print(
            "Data processed and ready to sent to sheets..............................."
        )
        print(
            batch_update_sheet(
                sheets_service,
                spreadsheet_id=spreadsheet_id,
                data=processed_data_for_sheets,
            )
        )
        result = over_all_result(spreadsheet_id)
        return jsonify({"message": "Success" , "result":result}), 200
    except Exception as e:
        print(f"Calculate result error: {e}")
        return jsonify({"message": "Failed to calculate result."}), 400


@app.route("/internal/over_all_result")
def over_all_result(spreadsheet_id):
    try:
        sheets_service = authorize_client()[2]
        sheet_ranges = ['Service Level Sizing!A1:F30', 'FINAL SIZING SUMMARY!A2:H18']
        over_all_result = batch_get_sheet_data(client=sheets_service, spreadsheet_id=spreadsheet_id, sheet_ranges=sheet_ranges)
        Service_Level_Sizing = over_all_result["'Service Level Sizing'"]
        Final_Sizing_Summary = over_all_result["'FINAL SIZING SUMMARY'"]

        service_level_headers = Service_Level_Sizing[0]
        service_level_rows = Service_Level_Sizing[1:]
        final_sizing_header_1 = Final_Sizing_Summary[1][0:7]
        final_sizing_rows_1 = [row[:-1] if i < 4 else row for i, row in enumerate(Final_Sizing_Summary[2:7])]
        final_sizing_header_2 = Final_Sizing_Summary[10]
        final_sizing_rows_2 = Final_Sizing_Summary[11:18]

        
        table_data = {
            "service_level_headers": service_level_headers,
            "service_level_rows": service_level_rows,
            "final_sizing_header_1": final_sizing_header_1,
            "final_sizing_rows_1": final_sizing_rows_1,
            "final_sizing_header_2": final_sizing_header_2,
            "final_sizing_rows_2": final_sizing_rows_2
        }
        page_info = {
            "title": f"vuSizing Calc",
            "description": "Template page",
            "user_info": {
                "user_personal_info": "Not available",
                "template_name": "Not available",
            },
            "table_data": table_data
        }
        return render_template("over_all_sizing.html", page_info=page_info)
    except Exception as e:
        print(f"Overall result error: {e}")
        return jsonify({"message": "Failed to fetch overall result."}), 500




@login_required
@app.route("/save_inputs/<template_name>" , methods=["POST"])
def save_inputs(template_name):
    try:
        user_personal_info = get_user_info(session["access_token"])
        detail_user_info = find_user_by_email(email=user_personal_info["email"])
        data = request.get_json()
        form_data = data.get("form_data")
        form_status = data.get("form_status")
       
        template_data_from_db = find_user_template_data(email=user_personal_info["email"], template_name=template_name)

        if template_data_from_db:
            print("Mapping form values to db template values")
            mapped_data = map_form_values_db_template_values(form_data, template_data_from_db)
    
            new_template_data = {
                "form_status" : form_status,
                "form_data" : mapped_data
            }
          
            update_template_data_by_frontend(email=user_personal_info["email"], template_name=template_name, new_template_data=new_template_data)
            return jsonify({"message": "Success"}), 200
        else:
            return jsonify({"message": "Failed to save inputs."}), 400
    except Exception as e:
        print(f"Save inputs error: {e}")
        return jsonify({"message": "Failed to save inputs."}), 400

request_count = 0
lock = Lock()

@app.route('/process_sheet')
def process_sheet():
    global request_count
    
    # Step 1: Acquire the lock to safely update request_count
    with lock:
        request_count += 1
        # Check if we have processed 4 requests
        if request_count % 4 == 0:
            time.sleep(1)  # Introduce a 1-second delay

    # Step 2: Authorize the client
    client, drive_service, sheets_service = authorize_client()

    # Step 3: Create a copy of the master spreadsheet
    spreadsheet_id = "1ntX-jpnNnfakFhjOdpyISky4IEfj4pA25NE9usUEewo"

    data = [
        {'range': 'vuLogx!D3:D6', 'values': [[0.0], [0.0], ['True']]},
        {'range': 'vuBJM!D3:D6', 'values': [[0.0], [0.0], [0.0]]},
        {'range': 'vuInfra!D3:D16', 'values': [[0.0], [0.0], [0.0], [0.0], [0.0], [0.0], [0.0], [0.0], [0.0], [0.0], [0.0], [0.0], [0.1]]},
        {'range': 'vuTraces!D3:D8', 'values': [[0.0], [0.0], [0.0], [0.0], ['']]},
        {'range': 'vuCoreML!D3:D7', 'values': [[0.0], [0.0], [0.0], ['True']]},
        {'range': 'General Inputs!C3:C6', 'values': [['True'], [0.0], [0], [0]]},
        {'range': 'General Inputs!B11:E11', 'values': [[10, 10, 10, 10]]}
    ]
    
    batch_update_sheet(sheets_service, spreadsheet_id=spreadsheet_id, data=data)
    sheet_ranges = ['Service Level Sizing!A1:F30', 'FINAL SIZING SUMMARY!A2:H18']
    # Step 4: Get the results from the specified sheets
    data = batch_get_sheet_data(client=sheets_service , spreadsheet_id=spreadsheet_id, sheet_ranges=sheet_ranges)

    # Process results as needed (e.g., format them)
    results = {
        "data":data
    }


    # Return the results
    return jsonify({
        "message": "Spreadsheet processed successfully.",
        "results": results
    }), 200



@login_required
@app.route("/internal/logout")
def logout():
    session.clear()
    flash("You have been logged out.")
    return redirect("/internal/home")


def get_user_info(access_token):
    try:
        response = requests.get(
            "https://www.googleapis.com/oauth2/v3/userinfo",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch user info: {e}")
        return None




if __name__ == "__main__":
    create_table()
    app.run(debug=True, port=3389)
