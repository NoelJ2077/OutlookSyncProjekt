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

// Display contacts on load dashboard.
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

});

// excluding fields. 
const excludeFields = ["categories", "parentFolderId", "changeKey", "createdDateTime", "fileAs", "id", "lastModifiedDateTime", "photo", "yomiCompanyName", "yomiGivenName", "yomiSurname", "imAddresses"];

async function openCreateModal(el) {
  const schema = await fetch("/static/ressource.json").then(r => r.json());
  const formContainer = document.getElementById("dynamicFormFieldsC");
  console.log("Create a new contact");
  $('#createContactModal').modal('hide');

  formContainer.innerHTML = "";
  formContainer.style.display = "grid";
  formContainer.style.gridTemplateColumns = "1fr 1fr 1fr"; // 3 col's
  formContainer.style.gap = "12px 16px"; // vertical, horizontal
  formContainer.style.padding = "4px";

  for (const [field, type] of Object.entries(schema)) {
    if (excludeFields.includes(field)) continue;

    let value = "";

    // complex data types have different handling. 
    if (field === "emailAddresses") {
      value = "default email@demo.com"; // TODO: split email into 3 different fields
    } else if (["businessPhones", "homePhones", "children", "categories", "imAddresses"].includes(field)) {
      value = "";
    } else if (["businessAddress", "homeAddress", "otherAddress"].includes(field)) {
      value = "street 123\n8000 Zürich\nCH";
    } else {
      value = "";
    }

    // Wrapper für das Feld
    const fieldWrapper = document.createElement("div");
    fieldWrapper.style.display = "flex";
    fieldWrapper.style.flexDirection = "column";

    const label = document.createElement("label");
    label.setAttribute("for", field);
    label.innerText = field;
    label.style.fontSize = "13px";
    label.style.marginBottom = "4px";
    label.style.fontWeight = "500";
    label.style.color = "#fff";

    let input;
    if (["businessAddress", "homeAddress", "otherAddress", "emailAddresses"].includes(field)) {
      input = document.createElement("textarea");
      input.rows = (field === "emailAddresses") ? 4 : 4;
      input.style.resize = "vertical";
    } else {
      input = document.createElement("input");
      input.type = "text";
      input.placeholder = "";
    }

    input.name = field;
    input.id = field;
    input.value = value;
    input.style.border = "none";
    input.style.borderBottom = "1px solid #ccc";
    input.style.padding = "4px 6px";
    input.style.fontSize = "14px";
    input.style.outline = "none";
    input.style.background = "transparent";
    input.style.width = "100%";

    fieldWrapper.appendChild(label);
    fieldWrapper.appendChild(input);
    formContainer.appendChild(fieldWrapper);
  }

  $('#createContactModal').modal('show');
}

async function openEditModal(el) {
  const contactId = el.getAttribute("data-contact-id");
  const contactName = el.getAttribute("data-contact-name");

  document.getElementById("contactIdToEdit").value = contactId;
  document.getElementById("contactNameToEdit").innerText = contactName; // None???
  console.log("edit contact: ", contactName)
  // get field, scheme
  const schema = await fetch("/static/ressource.json").then(r => r.json());
  
  // Lade Kontaktwerte vom Server
  const contactData = await fetch(`/get_contact/${contactId}`).then(r => r.json());

  const formContainer = document.getElementById("dynamicFormFieldsE");
  $('#editContactModal').modal('hide'); // Stattdessen verdecken (weil Bootstrap)

  
  // Clear container und setze auf Grid (2 Spalten)
  formContainer.innerHTML = "";  // Leeren nicht erlaubt, sonst error bei wieder öffnen da DOM = None
  formContainer.style.display = "grid";
  formContainer.style.gridTemplateColumns = "1fr 1fr 1fr"; // 3 col's
  formContainer.style.gap = "12px 16px"; // vertical, horizontal
  formContainer.style.padding = "4px";

  for (const [field, type] of Object.entries(schema)) {
    if (excludeFields.includes(field)) continue;

    let rawValue = contactData[field];
    let value = "";

    if (field === "emailAddresses" && Array.isArray(rawValue)) {
      value = rawValue
        .map(e => {
          const type = (e.name && e.name !== e.address) ? e.name : "default";
          return `${type}: ${e.address || ""}`;
        })
        .join("\n");
    }
    else if (["businessPhones", "homePhones", "children", "categories", "imAddresses"].includes(field)) {
    value = Array.isArray(rawValue) ? rawValue.join(", ") : "";
    } else if (["businessAddress", "homeAddress", "otherAddress"].includes(field)) {
      const { street = "", postalCode = "", city = "", countryOrRegion = "" } = rawValue || {};
      value = `${street}\n${postalCode} ${city}\n${countryOrRegion}`;
    } else if (["birthday", "createdDateTime", "lastModifiedDateTime"].includes(field)) {
      value = rawValue ? new Date(rawValue).toLocaleString() : "";
    } else if (typeof rawValue === "object" && rawValue !== null) {
      value = JSON.stringify(rawValue);
    } else {
      value = rawValue || "";
    }

    // Wrapper für das Feld
    const fieldWrapper = document.createElement("div");
    fieldWrapper.style.display = "flex";
    fieldWrapper.style.flexDirection = "column";

    const label = document.createElement("label");
    label.setAttribute("for", field);
    label.innerText = field;
    label.style.fontSize = "13px";
    label.style.marginBottom = "4px";
    label.style.fontWeight = "500";
    label.style.color = "#fff";

    let input;
    if (["businessAddress", "homeAddress", "otherAddress", "emailAddresses"].includes(field)) {
      input = document.createElement("textarea");
      input.rows = 4;
      input.style.resize = "vertical";
    } else if (field === "emailAddresses") { 
        input = document.createElement("textarea");
        input.rows = 3;
    } else {
      input = document.createElement("input");
      input.type = "text";
      input.placeholder = value;
    }

    input.name = field;
    input.id = field;
    input.value = value;
    input.style.border = "none";
    input.style.borderBottom = "1px solid #ccc";
    input.style.padding = "4px 6px";
    input.style.fontSize = "14px";
    input.style.outline = "none";
    input.style.background = "transparent";
    input.style.width = "100%";

    fieldWrapper.appendChild(label);
    fieldWrapper.appendChild(input);
    formContainer.appendChild(fieldWrapper);
  }

  $('#editContactModal').modal('show');
}

function openDeleteModal(el) {
  var contactId = el.getAttribute("data-contact-id");
  var contactName = el.getAttribute("data-contact-name");

  document.getElementById("contactIdToDelete").value = contactId;
  document.getElementById("contactNameToDelete").innerText = contactName;
  console.log("delete contact: ", contactName)

  $('#deleteContactModal').modal('show');

  window.location.hash = `delete_contact_${contactId}`;
}

// hide modals
function closeCreateModal() {
  $('#CreateContactModal').modal('hide');
}
function closeEditModal() {
  $('#editContactModal').modal('hide');
}
function closeDeleteModal() {
  $('#deleteContactModal').modal('hide');
}
