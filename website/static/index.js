// Initialize the navbar functionality
var navbarToggler = document.querySelector(".navbar-toggler");
var navbarContent = document.querySelector("#navbarContent");

navbarToggler.addEventListener("click", function () {
  navbarContent.classList.toggle("show");
});

$(document).ready(function () {
  $(".alert .btn-close").click(function () {
    $(this).closest(".alert").alert("close");
  });
});

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

document.getElementById("filter").addEventListener("change", function () {
  var filter = this.value;
  var startDateInput = document.getElementById("start-date");
  var endDateInput = document.getElementById("end-date");

  // Show or hide date inputs based on the selected filter
  if (filter === "range") {
    startDateInput.style.display = "block";
    endDateInput.style.display = "block";

    // Initialize Flatpickr on the date inputs
    flatpickr(startDateInput, {
      // Date format and options...
      // Date format
      dateFormat: "Y-m-d",

      // Minimum and maximum selectable dates
      minDate: "2000-01-01",
      maxDate: "2099-12-31",

      // Appearance
      altInput: true,
      altFormat: "F j, Y", // Display format in the input field
      allowInput: true,
      clickOpens: true,
    });

    flatpickr(endDateInput, {
      // Date format and options...
      // Date format
      dateFormat: "Y-m-d",

      // Minimum and maximum selectable dates
      minDate: "2000-01-01",
      maxDate: "2099-12-31",

      // Appearance
      altInput: true,
      altFormat: "F j, Y", // Display format in the input field
      allowInput: true,
      clickOpens: true,
    });
  } else {
    startDateInput.style.display = "none";
    endDateInput.style.display = "none";
  }
});

function togglePaymentMethod() {
  var paymentMethodSelect = document.getElementById("payment_method");
  var bankSelectDiv = document.getElementById("bank_select_div_expense");
  var cashSelectDiv = document.getElementById("cash_select_div_expense");

  if (paymentMethodSelect.value === "bank") {
    bankSelectDiv.style.display = "block";
    cashSelectDiv.style.display = "none";
  } else if (paymentMethodSelect.value === "cash") {
    bankSelectDiv.style.display = "none";
    cashSelectDiv.style.display = "block";
  } else {
    bankSelectDiv.style.display = "none";
    cashSelectDiv.style.display = "none";
  }
}

function togglePaymentMethodIncome() {
  var paymentMethodSelect = document.getElementById("payment_method");
  var bankSelectDiv = document.getElementById("bank_select_div_income");
  var cashSelectDiv = document.getElementById("cash_select_div_income");

  if (paymentMethodSelect.value === "bank") {
    bankSelectDiv.style.display = "block";
    cashSelectDiv.style.display = "none";
  } else if (paymentMethodSelect.value === "cash") {
    bankSelectDiv.style.display = "none";
    cashSelectDiv.style.display = "block";
  } else {
    bankSelectDiv.style.display = "none";
    cashSelectDiv.style.display = "none";
  }
}


document.getElementById("filter-button").addEventListener("click", function () {
  var filter = document.getElementById("filter").value;
  var startDate = document.getElementById("start-date").value;
  var endDate = document.getElementById("end-date").value;

  var data = { filter: filter };
  if (filter === "range") {
    data.start_date = startDate;
    data.end_date = endDate;
  }

  // Make an AJAX request to fetch filtered data
  fetch("/filter", {
    method: "POST",
    body: JSON.stringify(data),
    headers: {
      "Content-Type": "application/json",
    },
  })
    .then((response) => response.json())
    .then((data) => {
      // Update the table with filtered data
      var tableBody = document.getElementById("data").querySelector("tbody");
      tableBody.innerHTML = "";

      data.transactions.forEach((money) => {
        var row = document.createElement("tr");
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
    .catch((error) => console.error(error));
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

function deleteBank(bankId, csrfToken) {
  fetch(`/banks/${bankId}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": csrfToken,
    },
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.message === "Bank deleted successfully.") {
        location.reload(); // Refresh the page after successful deletion
      } else {
        console.log("Failed to delete the bank.");
      }
    })
    .catch((error) => {
      console.error("Error:", error);
    });
}
