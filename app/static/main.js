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


// delete a contact
document.addEventListener("DOMContentLoaded", function () {
  // Alle delete-Links auswählen
  const deleteLinks = document.querySelectorAll(".delete-contact");
  const modal = document.getElementById("deleteContactModal");
  const contactIdInput = document.getElementById("contact_id_input");
  const cancelButton = document.getElementById("cancelDelete");

  // EventListener auf alle delete-Links setzen
  deleteLinks.forEach(function (link) {
    link.addEventListener("click", function (event) {
      event.preventDefault(); // Link-Verhalten verhindern
      const contactId = this.getAttribute("data-contact-id");
      contactIdInput.value = contactId;
      modal.style.display = "block";
    });
  });

  // Modal schließen bei Klick auf "Abbrechen"
  cancelButton.addEventListener("click", function () {
    modal.style.display = "none";
  });

  // Optional: Klick außerhalb des Modals schließt es
  window.addEventListener("click", function (event) {
    if (event.target === modal) {
      modal.style.display = "none";
    }
  });
});

