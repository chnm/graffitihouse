// Conditionally display fields in the Admin view.
// Only show sender and receiver if Type is Letter. 

// Get the type field.
const type = document.getElementById('id_type');

// Get the fields.
let sender = document.getElementsByClassName('field-sender');
let receiver = document.getElementsByClassName('field-receiver');

// Hide the fields.
sender.style.display = 'none';
receiver.style.display = 'none';

// Show the fields if the type is Letter.
if (type.value === 'Letter') {
    sender.style.display = 'block';
    receiver.style.display = 'block';
}