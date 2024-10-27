# Frontend data
frontend_data = {
    "vuLogx": {
        "formData": [
            {"name": "vuLogx_Syslog Size per day(GB)", "value": "0.0"},
            {"name": "vuLogx_App Logs Size per day(GB)", "value": "0.0"},
            {"name": "vuLogx_Raw Logs storage", "value": "TRUE"}
        ]
    },
    "vuBJM": {
        "formData": [
            {"name": "vuBJM_Daily Transaction Volume", "value": "0.0"},
            {"name": "vuBJM_Transaction Rate (TPS)", "value": "0.0"},
            {"name": "vuBJM_Transaction Touchpoints", "value": "0.0"}
        ]
    },
    "vuInfra": {
        "formData": [
            {"name": "vuInfra_Servers", "value": "0.0"},
            {"name": "vuInfra_Network Devices", "value": "0.0"},
            {"name": "vuInfra_Storage Devices", "value": "0.0"},
            {"name": "vuInfra_Web Servers", "value": "0.0"},
            {"name": "vuInfra_Middleware", "value": "0.0"},
            {"name": "vuInfra_SQL Databases", "value": "0.0"},
            {"name": "vuInfra_NoSQL Databases", "value": "0.0"},
            {"name": "vuInfra_Netflow", "value": "0.0"},
            {"name": "vuInfra_Config Collections", "value": "0.0"},
            {"name": "vuInfra_Availability - Links, Hosts, Services and URL", "value": "0.0"},
            {"name": "vuInfra_Synthetic Monitoring Journeys", "value": "0.0"},
            {"name": "vuInfra_API Monitoring", "value": "0.0"},
            {"name": "vuInfra_Polling Interval (Seconds)", "value": "0.1"}
        ]
    },
    "vuTraces": {
        "formData": [
            {"name": "vuTraces_Transaction Volume per day", "value": "0.0"},
            {"name": "vuTraces_Transaction Rate (TPS)", "value": "0.0"},
            {"name": "vuTraces_Non Transactional JVMs/Instances", "value": "0.0"},
            {"name": "vuTraces_Transaction Touchpoints", "value": "0.0"},
            {"name": "vuTraces_Real User Monitoring - Concurrent Users", "value": ""}
        ]
    },
    "vuCoreML": {
        "formData": [
            {"name": "vuCoreML_Num of Signals", "value": "0.0"},
            {"name": "vuCoreML_Approx Num dimensions per signal", "value": "0.0"},
            {"name": "vuCoreML_Num Fields Per Signal", "value": "0.0"},
            {"name": "vuCoreML_LLM based Analytics", "value": "TRUE"}
        ]
    },
    "DataRetention": {
        "formData": [
            {"name": "DataRetention_Hot Search (Days)", "value": "10"},
            {"name": "DataRetention_Warm Search (Days)", "value": "10"},
            {"name": "DataRetention_Cold Search (Days)", "value": "10"},
            {"name": "DataRetention_Summarized Data Retention (Days)", "value": "10"}
        ]
    },
    "GeneralInputs": {
        "formData": [
            {"name": "GeneralInputs_High Availability ?", "value": "TRUE"},
            {"name": "GeneralInputs_Num of environments (DC/DR)", "value": "0.0"},
            {"name": "GeneralInputs_Num of vuSmartMaps users", "value": "0"},
            {"name": "GeneralInputs_Num Alerts", "value": "0"}
        ]
    }
}

# Existing database data
database_data = [
    {
        "template_name": "Shree Ganesh",
        "template_data": {
            "vuCoreML": {
                "Num of Signals": "",
                "Approx Num dimensions per signal": "",
                "Num Fields Per Signal": "",
                "LLM based Analytics": ""
            },
            "vuLogx": {
                "Syslog Size per day(GB)": "",
                "App Logs Size per day(GB)": "",
                "Raw Logs storage": ""
            },
            "vuBJM": {
                "Daily Transaction Volume": "",
                "Transaction Rate (TPS)": "",
                "Transaction Touchpoints": "",
                "Ingest touchpoint data ?": ""
            },
            "vuTraces": {
                "Transaction Volume per day": "",
                "Transaction Rate (TPS)": "",
                "Non Transactional JVMs/Instances": "",
                "Transaction Touchpoints": "",
                "Real User Monitoring - Concurrent Users": ""
            },
            "vuInfra": {
                "Servers": "",
                "Network Devices": "",
                "Storage Devices": "",
                "Web Servers": "",
                "Middleware": "",
                "SQL Databases": "",
                "NoSQL Databases": "",
                "Netflow": "",
                "Config Collections": "",
                "Availability - Links, Hosts, Services and URL": "",
                "Synthetic Monitoring Journeys": "",
                "API Monitoring": "",
                "Polling Interval (Seconds)": ""
            }
        }
    }
]

# Mapping function
def map_values(frontend_data, database_data):
    for component, data in frontend_data.items():
        for entry in data["formData"]:
            name = entry["name"]
            value = entry["value"]
            # Extract the relevant section of the database
            for template in database_data:
                if component in template["template_data"]:
                    field_name = name.split(f"{component}_")[-1]  # Remove component prefix
                    if field_name in template["template_data"][component]:
                        template["template_data"][component][field_name] = value

# Perform mapping
map_values(frontend_data, database_data)

# Display updated database data
import json
print(json.dumps(database_data, indent=4))
