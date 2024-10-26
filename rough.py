import json

# Sample form data structure
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
