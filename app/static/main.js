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
  console.log("Edit click:", contactId, contactName); // ok

  document.getElementById("contactIdToDelete").value = contactId;
  document.getElementById("contactNameToDelete").innerText = contactName;

  $('#deleteContactModal').modal('show');

  window.location.hash = `delete_contact_${contactId}`;
}

async function openEditModal(el) {
  const contactId = el.getAttribute("data-contact-id");
  const contactName = el.getAttribute("data-contact-name");
  document.getElementById("contactIdToEdit").value = contactId;
  document.getElementById("contactNameToEdit").innerText = contactName;

  // get field, scheme
  const schema = await fetch("/static/ressource.json").then(r => r.json());
  
  // Lade Kontaktwerte vom Server
  const contactData = await fetch(`/get_contact/${contactId}`).then(r => r.json());
  // err: http://localhost:5000/get_contact/contact_id(id) abbrevieated for display

  const formContainer = document.getElementById("dynamicFormFields");
  $('#editContactModal').modal('hide'); // Stattdessen verdecken (weil Bootstrap)

  // Felder, die wir ignorieren wollen
  const excludeFields = ["categories", "changekey", "createdDateTime", "fileAS", "parentFolderID"];

  // Clear container und setze auf Grid (2 Spalten)
  formContainer.innerHTML = "";  // Leeren nicht erlaubt, sonst error bei wieder öffnen da DOM = None
  formContainer.style.display = "grid";
  formContainer.style.gridTemplateColumns = "1fr 1fr 1fr"; // 3 col's
  formContainer.style.gap = "12px 16px"; // vertical, horizontal
  formContainer.style.padding = "4px";

  for (const [field, type] of Object.entries(schema)) {
    if (excludeFields.includes(field)) continue;

    let value = contactData[field] || "";
    if (Array.isArray(value)) {
      value = value.join(", ");
    } else if (typeof value === 'object' && value !== null) {
      // extra format for fields like addressfields
      if (["businessAddress", "homeAddress", "otherAddress"].includes(field)) {
        const { street = "", postalCode = "", city = "", countryOrRegion = "" } = value;
        value = `${street},  ${postalCode},  ${city},  ${countryOrRegion}`;
      } else {
        value = JSON.stringify(value);
      }
    }

    // Wrapper für ein Feld
    const fieldWrapper = document.createElement("div");
    fieldWrapper.style.display = "flex";
    fieldWrapper.style.flexDirection = "column";

    // Label
    const label = document.createElement("label");
    label.setAttribute("for", field);
    label.innerText = field;
    label.style.fontSize = "13px";
    label.style.marginBottom = "4px";
    label.style.fontWeight = "500";
    label.style.color = "#fff";

    // Input mit Unterstrich-Optik
    const input = document.createElement("input");
    input.name = field;
    input.id = field;
    input.type = "text";
    input.placeholder = value;
    input.style.border = "none";
    input.style.borderBottom = "1px solid #ccc";
    input.style.padding = "4px 6px";
    input.style.fontSize = "14px";
    input.style.outline = "none";
    input.style.background = "transparent";
    // make size 80px
    input.style.width = "100%";

    // Zusammenbauen
    fieldWrapper.appendChild(label);
    fieldWrapper.appendChild(input);
    formContainer.appendChild(fieldWrapper);
  }




  $('#editContactModal').modal('show');
}


// hide modals onclick
function closeEditModal() {
  $('#editContactModal').modal('hide');
}
function closeDeleteModal() {
  $('#deleteContactModal').modal('hide');
}
