 // Tab functionality
 const k8s_tab = document.getElementById('k8s_tab');
 const vms_tab = document.getElementById('vms_tab');
 const k8s_table = document.getElementById('k8s_table');
 const vms_table = document.getElementById('vms_table');

 // Function to switch tabs
 function activateTab(tab, contentToShow, contentToHide) {
     // Reset all tabs
     k8s_tab.classList.remove('bg-blue-600');
     vms_tab.classList.remove('bg-blue-600');
     // Highlight active tab
     tab.classList.add('bg-blue-600');

     // Show and hide tables
     contentToShow.classList.remove('hidden');
     contentToHide.classList.add('hidden');
 }

 // Event listeners for tabs
 k8s_tab.addEventListener('click', () => activateTab(k8s_tab, k8s_table, vms_table));
 vms_tab.addEventListener('click', () => activateTab(vms_tab, vms_table, k8s_table));

 var formFlags = {
    vuLogx: false,
    vuBJM: false,
    vuInfra: false,
    vuTraces: false,
    vuCoreML: false,
    DataRetention: false,
    GeneralInputs: false
};

function toggle_form(form_name) {
    var formSection = document.getElementById("form-" + form_name);
    
    // Toggle the display style of the section
    if (formSection.style.display === "none") {
        formSection.style.display = "block"; // Show the section
        setInputsRequired(formSection, true); // Set inputs to required
    } else {
        formSection.style.display = "none"; // Hide the section
        setInputsRequired(formSection, false); // Remove required from inputs
    }
    
    // Toggle the flag in formFlags
    formFlags[form_name] = !formFlags[form_name];
    
    // Check if submit button should be enabled
    checkSubmitButton();
    console.log(formFlags);
}

function setInputsRequired(section, isRequired) {
    // Find all inputs in the section and set required attribute
    $(section).find('input').each(function() {
        if ($(this).attr('type') !== 'checkbox') {
            $(this).prop('required', isRequired); // Set required
        }
    });
}

function checkSubmitButton() {
    let isAnyInputValid = false;

    for (const key in formFlags) {
        if (formFlags[key]) {
            // Check for valid inputs in the visible sections
            const inputs = $(`#form-${key}`).find('input');
            inputs.each(function() {
                if ($(this).is(':checkbox')) {
                    // Checkbox is valid if checked
                    if ($(this).is(':checked')) {
                        isAnyInputValid = true;
                    }
                } else {
                    // Numeric and text inputs are valid if they have a value
                    if ($(this).val().trim() !== '') {
                        isAnyInputValid = true;
                    }
                }
            });
        }
    }

    // Enable or disable the submit button based on the validity of the inputs
    $('#main_form').prop('disabled', !isAnyInputValid);
    
    // Toggle button styles based on state
    if (isAnyInputValid) {
        $('#main_form').removeClass('btn-disabled').addClass('btn-enabled');
    } else {
        $('#main_form').removeClass('btn-enabled').addClass('btn-disabled');
    }
}

$('input').on('input change', function() {
    checkSubmitButton(); // Check button validity on input changes
});

$('#main_form').on('click', function(e) {
    e.preventDefault(); // Prevent default form submission
    var data = {}; // Initialize an empty object to store form data
    $('#loader').fadeIn('fast'); 
    // Loop over formFlags to gather data from selected sections
    for (var key in formFlags) {
            // Serialize each section’s form data as an array of {name, value} objects
            var formData = $(`#form-${key}`).serializeArray();               
            // Add each section to `data` with the required structure
            data[key] = { "formData": formData };
    }

    $.ajax({
        type: 'POST',
        url: '/calculate',
        contentType: 'application/json', // Set content type to JSON
        data: JSON.stringify(data), // Send data as a JSON string
        success: function(response) {
            getting_results();
        },
        error: function(xhr, status, error) {
            $('#loader').fadeIn('slow');
            console.error("AJAX Error: ", error); // Log any error
        }
    });
});

// Result handling
// Result for Service Level Sizing
function getting_results() {
    $('#loader').fadeIn('fast');

    // Define both AJAX requests as promises
    const serviceLevelSizingRequest = $.ajax({
        type: 'GET',
        url: '/results/service_level_sizing',
    });

    const finalSizingRequest = $.ajax({
        type: 'GET',
        url: '/results/final_sizing',
    });

    // Execute both AJAX requests concurrently
    Promise.all([serviceLevelSizingRequest, finalSizingRequest])
        .then((responses) => {
            // Both requests were successful
            const [serviceLevelResponse, finalSizingResponse] = responses;
            $('#service_level_sizing_table').html(serviceLevelResponse);
            $('#final_sizing_table').html(finalSizingResponse);
            $('#loader').fadeOut('slow');  // Hide the loader when both requests are complete
            console.log("All requests completed successfully.");
        })
        .catch((error) => {
            // One or both requests failed
            console.error("AJAX Error: ", error);
            $('#loader').fadeOut('slow');  // Hide the loader on error as well
        });
}

 // Tab functionality
 const final_sizing_tab = document.getElementById('final_sizing_tab');
 const service_level_sizing_tab = document.getElementById('service_level_sizing_tab');
 const final_sizing_table = document.getElementById('final_sizing_table');
 const service_level_sizing_table = document.getElementById('service_level_sizing_table');

 // Function to switch tabs
 function main_activateTab(tab, contentToShow, contentToHide) {
     // Reset all tabs
     final_sizing_tab.classList.remove('bg-blue-600');
     service_level_sizing_tab.classList.remove('bg-blue-600');
     // Highlight active tab
     tab.classList.add('bg-blue-600');

     // Show and hide tables
     contentToShow.classList.remove('hidden');
     contentToHide.classList.add('hidden');
 }

 // Event listeners for tabs
 final_sizing_tab.addEventListener('click', () => main_activateTab(final_sizing_tab, final_sizing_table, service_level_sizing_table));
 service_level_sizing_tab.addEventListener('click', () => main_activateTab(service_level_sizing_tab, service_level_sizing_table, final_sizing_table));
