
// Get the modal
var modal = document.getElementById("addexpensemodal");

// Get the button that opens the modal
var btn = document.getElementById("addexpense-btn");

// Get the <span> element that closes the modal
var span = document.getElementsByClassName("close")[0];

// When the user clicks on the button, open the modal
btn.onclick = function () {
  modal.style.display = "block";
};

// When the user clicks on <span> (x), close the modal
span.onclick = function () {
  modal.style.display = "none";
};

// When the user clicks anywhere outside of the modal, close it
window.onclick = function (event) {
  if (event.target == modal) {
    modal.style.display = "none";
  }
};

// Get the income modal
var inmodal = document.getElementById("addincomemodal");
var inbtn = document.getElementById("addincome-btn");
var inspan = document.getElementsByClassName("closein")[0];

inbtn.onclick = function () {
  inmodal.style.display = "block";
};

inspan.onclick = function () {
  inmodal.style.display = "none";
};

window.onclick = function (event) {
  if (event.target == inmodal) {
    inmodal.style.display = "none";
  }
};


document.getElementById('filter-button').addEventListener('click', function() {
  var filter = document.getElementById('filter').value;
  var startDate = document.getElementById('start-date').value;
  var endDate = document.getElementById('end-date').value;

  var data = { filter: filter };
  if (filter === 'range') {
    data.start_date = startDate;
    data.end_date = endDate;
  }

  // Make an AJAX request to fetch filtered data
  fetch('/filter', {
    method: 'POST',
    body: JSON.stringify(data),
    headers: {
      'Content-Type': 'application/json'
    }
  })
  .then(response => response.json())
  .then(data => {
    // Update the table with filtered data
    var tableBody = document.getElementById('data').querySelector('tbody');
    tableBody.innerHTML = '';

    data.transactions.forEach(money => {
      var row = document.createElement('tr');
      row.innerHTML = `
        <td>${money.transaction_id}</td>
        <td>${money.transaction_name}</td>
        <td>${money.amount}</td>
        <td>${money.category}</td>
        <td>${money.date}</td>
        <td>${money.transaction_type}</td>
      `;
      tableBody.appendChild(row);
    });
  })
  .catch(error => console.error(error));
});



function deleteTransaction(transactionId, csrfToken) {
  fetch(`/delete/${transactionId}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": csrfToken,
    },
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.message === "Transaction deleted successfully.") {
        location.reload(); // Refresh the page after successful deletion
      } else {
        console.log("Failed to delete the transaction.");
      }
    })
    .catch((error) => {
      console.error("Error:", error);
    });
}
