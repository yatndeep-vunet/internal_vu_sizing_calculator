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
)
from tabulate import tabulate
from helper_functions import load_and_collect_form_inputs, get_data_for_sheet_with_form , map_form_values_db_template_values

form_inputs = "./form_inputs/form_inputs.json"
from dotenv import load_dotenv

app = Flask(__name__)
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


@app.route("/signin")
def signin():
    if not oauth_flow:
        return "OAuth configuration is missing. Cannot initiate signin.", 500

    oauth_flow.redirect_uri = url_for("oauth2callback", _external=True).replace(
        "http://", "http://"
    )
    authorization_url, state = oauth_flow.authorization_url()
    session["state"] = state
    return redirect(authorization_url)


@app.route("/callback")
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


@app.route("/")
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


@app.route("/create_template", methods=["POST"])
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

        new_template_data = {
            "template_name": template_name,
            "template_data": load_and_collect_form_inputs(form_inputs),
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


@app.route("/template/<template_name>")
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
        }
        return render_template("template.html", page_info=page_info)
    except Exception as e:
        print(f"Template page error: {e}")
        return (
            "An error occurred while fetching the template. Please try again later.",
            500,
        )


@app.route("/calculate", methods=["POST"])
def calculate_result():
    try:
        user_personal_info = get_user_info(session["access_token"])
        detail_user_info = find_user_by_email(email=user_personal_info["email"])
        spreadsheet_id = detail_user_info[3]
        form_data = request.get_json()  # Parse JSON data
        print(form_data)
        gspread_client, drive_service, sheets_service = authorize_client()     
        if form_data is None:
            return jsonify({"message": "No data received."}), 400
        # print("Form Data from frontend:", form_data)  # Process form_data as needed
        print("Data is under processing ..............................................")
        # Actually what happens here is that we are getting the data from the frontend and then we are processing it
        # Process it to make it ready to be sent to the sheets
        processed_data_for_sheets = get_data_for_sheet_with_form(form_data)
        print(processed_data_for_sheets)
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
        return jsonify({"message": "Success"}), 200
    except Exception as e:
        print(f"Calculate result error: {e}")
        return jsonify({"message": "Failed to calculate result."}), 400


@app.route("/results/service_level_sizing")
@login_required
def service_level_sizing_results():
    try:
        user_personal_info = get_user_info(session["access_token"])
        detail_user_info = find_user_by_email(email=user_personal_info["email"])
        client, *other_values = authorize_client()  # Adjust unpacking here
        spreadsheet_id = detail_user_info[3]

        data = get_sheet_data_with_sheet_name(
            client=client,
            spreadsheet_id=spreadsheet_id,
            sheet_name="Service Level Sizing",
        )
        # print(data)
        headers, rows = data[0], data[1:]
        # First extract the data till column F
        row_data_till_column_F = [row[:6] for row in data[1:]]
        header_till_column_F = headers[:6]

        # Now reorder the data to have columns in the order of A, E , B, C, F, D
        new_order_indices = [0, 5, 1, 2, 3, 4]

        # Reorder the headers and row data to match the new column order
        reordered_headers = [header_till_column_F[i] for i in new_order_indices]
        reordered_rows = [
            [row[i] for i in new_order_indices] for row in row_data_till_column_F
        ]

        html_content = render_template(
            "service_level_results.html", headers=reordered_headers, rows=reordered_rows
        )
        # print(tabulated_data)
        return html_content
    except Exception as e:
        print(f"Results page error: {e}")
        return "An error occurred while fetching results. Please try again later.", 500


@app.route("/results/final_sizing")
def node_sizing_summary_results():
    try:
        client, *other_values = authorize_client()
        user_personal_info = get_user_info(session["access_token"])
        detail_user_info = find_user_by_email(email=user_personal_info["email"])
        spreadsheet_id = detail_user_info[3]
      
        # Get data for the first table
        data = get_sheet_data_with_sheet_name(
            client=client,
            spreadsheet_id=spreadsheet_id,
            sheet_name="FINAL SIZING SUMMARY",
        )

        # There are 2 tables in the sheet, so extract data for both

        headers_1, rows_1 = data[2], data[3:8]
        headers_2, rows_2 = data[11], data[12:18]

        # Render template with both tables' headers and rows
        return render_template(
            "final_sizing_results.html",
            headers_1=headers_1,
            rows_1=rows_1,
            headers_2=headers_2,
            rows_2=rows_2,
        )
    except Exception as e:
        print(f"Results page error: {e}")
        return "An error occurred while fetching results. Please try again later.", 500

@login_required
@app.route("/save_inputs/<template_name>" , methods=["POST"])
def save_inputs(template_name):
    try:
        user_personal_info = get_user_info(session["access_token"])
        detail_user_info = find_user_by_email(email=user_personal_info["email"])
        form_data = request.get_json()
        print("Template Name:", template_name)
        template_data_from_db = find_user_template_data(email=user_personal_info["email"], template_name=template_name)
        if template_data_from_db:
            print("Mapping form values to db template values")
            mapped_data = map_form_values_db_template_values(form_data, template_data_from_db)
            update_template_data_by_frontend(email=user_personal_info["email"], template_name=template_name, new_template_data=mapped_data)
            return jsonify({"message": "Success"}), 200
        else:
            return jsonify({"message": "Failed to save inputs."}), 400
    except Exception as e:
        print(f"Save inputs error: {e}")
        return jsonify({"message": "Failed to save inputs."}), 400

@login_required
@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.")
    return redirect("/")


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
    app.run(debug=True, port=5000)
