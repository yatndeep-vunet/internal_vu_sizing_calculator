from database import create_table, insert_user, read_users, delete_user , find_user_template_data
from helper_functions import map_form_values_db_template_values
email="yatndeep@vunetsystems.com"
# # Step 1: Create the table if it does not exist
# create_table()

# # Step 2: Insert a user
# #result = delete_user(email="yatndeep@vunetsystems.com")
# print(result)  # Should show success or an error message

# # Step 3: Read users
# users = read_users()
# print(users)  # Should show Alice in the list 
# 
template_data_from_db = find_user_template_data(email,"Shree Ganesh")  # Should show the user's data

form_data = {'vuLogx': {'formData': [{'name': 'vuLogx_Syslog Size per day(GB)', 'value': '0.0'}, {'name': 'vuLogx_App Logs Size per day(GB)', 'value': '0.0'}, {'name': 'vuLogx_Raw Logs storage', 'value': 'TRUE'}]}, 'vuBJM': {'formData': [{'name': 'vuBJM_Daily Transaction Volume', 'value': '0.0'}, {'name': 'vuBJM_Transaction Rate (TPS)', 'value': '0.0'}, {'name': 'vuBJM_Transaction Touchpoints', 'value': '0.0'}]}, 'vuInfra': {'formData': [{'name': 'vuInfra_Servers ', 'value': '0.0'}, {'name': 'vuInfra_Network Devices ', 'value': '0.0'}, {'name': 'vuInfra_Storage Devices', 'value': '0.0'}, {'name': 'vuInfra_Web Servers', 'value': '0.0'}, {'name': 'vuInfra_Middleware ', 'value': '0.0'}, {'name': 'vuInfra_SQL Databases', 'value': '0.0'}, {'name': 'vuInfra_NoSQL Databases', 'value': '0.0'}, {'name': 'vuInfra_Netflow ', 'value': '0.0'}, {'name': 'vuInfra_Config Collections', 'value': '0.0'}, {'name': 'vuInfra_Availability  - Links, Hosts, Services and URL', 'value': '0.0'}, {'name': 'vuInfra_Synthetic Monitoring Journeys', 'value': '0.0'}, {'name': 'vuInfra_API Monitoring', 'value': '0.0'}, {'name': 'vuInfra_Polling Interval (Seconds)', 'value': '0.1'}]}, 'vuTraces': {'formData': [{'name': 'vuTraces_Transaction Volume per day', 'value': '0.0'}, {'name': 'vuTraces_Transaction Rate (TPS)', 'value': '0.0'}, {'name': 'vuTraces_Non Transactional JVMs/Instances', 'value': '0.0'}, {'name': 'vuTraces_Transaction Touchpoints', 'value': '0.0'}, {'name': 'vuTraces_Real User Monitoring - Concurrent Users', 'value': ''}]}, 'vuCoreML': {'formData': [{'name': 'vuCoreML_Num of Signals', 'value': '0.0'}, {'name': 'vuCoreML_Approx Num dimensions per signal', 'value': '0.0'}, {'name': 'vuCoreML_Num Fields Per Signal', 'value': '0.0'}, {'name': 'vuCoreML_LLM based Analytics', 'value': 'TRUE'}]}, 'DataRetention': {'formData': [{'name': 'DataRetention_Hot Search (Days)', 'value': '10'}, {'name': 'DataRetention_Warm Search (Days)', 'value': '10'}, {'name': 'DataRetention_Cold Search (Days)', 'value': '10'}, {'name': 'DataRetention_Summarized Data Retention (Days)', 'value': '10'}]}, 'GeneralInputs': {'formData': [{'name': 'GeneralInputs_High Availability ?', 'value': 'TRUE'}, {'name': 'GeneralInputs_Num of environments (DC/DR)', 'value': '0.0'}, {'name': 'GeneralInputs_Num of vuSmartMaps users', 'value': '0'}, {'name': 'GeneralInputs_Num Alerts', 'value': '0'}]}}

template_data = map_form_values_db_template_values(form_data, template_data_from_db)

print(template_data)  # Should show the updated template data