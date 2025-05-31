//main.js
document.addEventListener('DOMContentLoaded', function() {
    const userElement = document.querySelector('.user_role');
    if (userElement) {
        const role = userElement.textContent.trim();
        userElement.style.fontStyle = 'italic';
        userElement.style.fontWeight = 'bold';
        
        if (role === 'admin') {
            userElement.style.color = 'rgb(156, 123, 203)';
        } else if (role === 'user') {
            userElement.style.color = 'rgb(40, 150, 40)';
        } else if (role === 'Guest') {
            userElement.style.color = 'rgb(179, 172, 99)';
        }

    }
});

// Display contacts. 
document.addEventListener('DOMContentLoaded', function() {
  const modal     = document.getElementById('editContactModal');
  const form      = document.getElementById('editContactForm');
  const cancelBtn = document.getElementById('cancelEdit');
  const idInput   = document.getElementById('contact_id_input');

  // Schema als JS-Variable (in dashboard.html direkt vor main.js einfügen):
  // <script>const SCHEMA = {{ schema|tojson|safe }};</script>
  // Oder lade es als globales window.SCHEMA

  document.querySelectorAll('.edit-contact').forEach(btn => {
    btn.addEventListener('click', e => {
      e.preventDefault();
      const contactId = btn.dataset.contactId;

      // Modal öffnen und ID setzen
      modal.style.display = 'block';
      idInput.value = contactId;

      // Kontaktdaten holen
      fetch(`/contact/${contactId}`)
        .then(r => r.json())
        .then(data => {
          // Für jedes Feld im Schema das passende Input befüllen
          Object.keys(SCHEMA).forEach(field => {
            const input = document.getElementById(field);
            if (!input) return;
            // falls Array oder Objekt: JSON stringify, sonst String
            if (Array.isArray(data[field]) || typeof data[field] === 'object') {
              input.value = JSON.stringify(data[field]);
            } else {
              input.value = data[field] || '';
            }
          });
        })
        .catch(err => {
          console.error('Error loading contact:', err);
          modal.style.display = 'none';
        });
    });
  });

  // Abbrechen
  cancelBtn.addEventListener('click', () => modal.style.display = 'none');
  modal.addEventListener('click', e => {
    if (e.target === modal) modal.style.display = 'none';
  });
});


function openDeleteModal(el) {
  var contactId = el.getAttribute("data-contact-id");
  var contactName = el.getAttribute("data-contact-name");

  document.getElementById("contactIdToDelete").value = contactId;
  document.getElementById("contactNameToDelete").innerText = contactName;

  $('#deleteContactModal').modal('show');

  window.location.hash = `delete_contact_${contactId}`;
}

function openEditModal(el) {
  var contactId = el.getAttribute("data-contact-id");
  var contactName = el.getAttribute("data-contact-name");

  document.getElementById("contactIdToEdit").value = contactId;
  document.getElementById("contactNameToEdit").innerText = contactName;

  // bootstrap view
  $('#editContactModal').modal('show');

  // set id into url (optional)
  window.location.hash = `edit_contact_${contactId}`;
}


// hide modals onclick
function closeEditModal() {
  $('#editContactModal').modal('hide');
}
function closeDeleteModal() {
  $('#deleteContactModal').modal('hide');
}
