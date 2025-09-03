(function($) {
    'use strict';
    
    // Wait for both document ready and django.jQuery
    function initStationAdmin() {
        // Function to toggle decoding fields based on Analog/Digital selection
        function toggleDecodingFields() {
            var analogChecked = $('#id_Analog').is(':checked');
            var digitalChecked = $('#id_Digital').is(':checked');
            
            // Get all decoding checkboxes
            var decodingFields = ['#id_FT8', '#id_FT4', '#id_RTTY', '#id_CW'];
            
            if (analogChecked) {
                // If Analog is selected, disable and gray out decoding fields
                // Also uncheck all decoding fields
                decodingFields.forEach(function(fieldId) {
                    $(fieldId).prop('disabled', true);
                    $(fieldId).prop('checked', false);
                    $(fieldId).closest('.form-row').addClass('disabled-field');
                });
            } else if (digitalChecked) {
                // If Digital is selected, enable decoding fields
                decodingFields.forEach(function(fieldId) {
                    $(fieldId).prop('disabled', false);
                    $(fieldId).closest('.form-row').removeClass('disabled-field');
                });
            } else {
                // If neither is selected, enable decoding fields
                decodingFields.forEach(function(fieldId) {
                    $(fieldId).prop('disabled', false);
                    $(fieldId).closest('.form-row').removeClass('disabled-field');
                });
            }
        }
        
        // Add CSS for disabled fields
        $('<style>')
            .prop('type', 'text/css')
            .html(`
                .disabled-field {
                    opacity: 0.5;
                    background-color: #f5f5f5;
                }
                .disabled-field input[type="checkbox"] {
                    cursor: not-allowed;
                }
                .disabled-field label {
                    color: #999;
                }
            `)
            .appendTo('head');
        
        // Initial call to set up the state
        toggleDecodingFields();
        
        // Bind events to Analog and Digital checkboxes
        $('#id_Analog, #id_Digital').on('change', function() {
            toggleDecodingFields();
        });
        
        // Function to format frequency with dots (max 2 dots)
        function formatFrequency(input) {
            console.log('Formatting frequency:', input.value);
            var value = input.value.replace(/\./g, '').replace(/\s/g, '');
            console.log('Cleaned value:', value);
            
            if (value.length >= 3) {
                var formatted = '';
                var dotCount = 0;
                for (var i = 0; i < value.length; i++) {
                    if (i > 0 && (value.length - i) % 3 === 0 && dotCount < 2) {
                        formatted += '.';
                        dotCount++;
                    }
                    formatted += value[i];
                }
                console.log('Formatted value:', formatted);
                input.value = formatted;
            }
        }
        
        // Bind blur event to frequency field
        $('#id_Frequency').on('blur', function() {
            console.log('Frequency field blur event triggered');
            formatFrequency(this);
        });
        
        // Also try on input event for immediate feedback
        $('#id_Frequency').on('input', function() {
            console.log('Frequency field input event triggered');
            // Don't format on every keystroke, just log
        });
    }
    
    // Try multiple ways to initialize
    if (typeof django !== 'undefined' && django.jQuery) {
        django.jQuery(document).ready(initStationAdmin);
    } else if (typeof $ !== 'undefined') {
        $(document).ready(initStationAdmin);
    } else {
        document.addEventListener('DOMContentLoaded', function() {
            // Fallback to vanilla JavaScript
            console.log('Using vanilla JavaScript fallback');
            
            var freqField = document.getElementById('id_Frequency');
            if (freqField) {
                console.log('Frequency field found with vanilla JS');
                
                function formatFrequency(input) {
                    console.log('Formatting frequency:', input.value);
                    var value = input.value.replace(/\./g, '').replace(/\s/g, '');
                    console.log('Cleaned value:', value);
                    
                    if (value.length >= 3) {
                        var formatted = '';
                        var dotCount = 0;
                        for (var i = 0; i < value.length; i++) {
                            if (i > 0 && (value.length - i) % 3 === 0 && dotCount < 2) {
                                formatted += '.';
                                dotCount++;
                            }
                            formatted += value[i];
                        }
                        console.log('Formatted value:', formatted);
                        input.value = formatted;
                    }
                }
                
                freqField.addEventListener('blur', function() {
                    console.log('Vanilla JS blur event triggered');
                    formatFrequency(this);
                });
            } else {
                console.log('Frequency field not found with vanilla JS');
            }
        });
    }
})(typeof django !== 'undefined' ? django.jQuery : (typeof $ !== 'undefined' ? $ : null)); 