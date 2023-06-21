// Inicialize a funcionalidade da barra de navegação
const navbarToggler = document.querySelector(".navbar-toggler");
const navbarContent = document.querySelector("#navbarContent");

navbarToggler.addEventListener("click", () => {
  navbarContent.classList.toggle("show");
});

$(document).ready(function () {
  $(".alert .btn-close").click(function () {
    $(this).closest(".alert").alert("close");
  });
});

// Obtenha o modal
const addExpenseModal = document.getElementById("addexpensemodal");
const addIncomeModal = document.getElementById("addincomemodal");

// Obtenha o botão que abre o modal
const addExpenseBtn = document.getElementById("addexpense-btn");
const addIncomeBtn = document.getElementById("addincome-btn");

// Obtenha o elemento <span> que fecha o modal
const expenseCloseBtn = document.getElementsByClassName("close")[0];
const incomeCloseBtn = document.getElementsByClassName("closein")[0];

// Quando o usuário clicar no botão, abra o modal
addExpenseBtn.onclick = () => {
  addExpenseModal.style.display = "block";
};

addIncomeBtn.onclick = () => {
  addIncomeModal.style.display = "block";
};

// Quando o usuário clicar no <span> (x), feche o modal
expenseCloseBtn.onclick = () => {
  addExpenseModal.style.display = "none";
};

incomeCloseBtn.onclick = () => {
  addIncomeModal.style.display = "none";
};

// Quando o usuário clicar fora do modal, feche-o
window.onclick = (event) => {
  if (event.target == addExpenseModal) {
    addExpenseModal.style.display = "none";
  }

  if (event.target == addIncomeModal) {
    addIncomeModal.style.display = "none";
  }
};

// Obtenha os campos de seleção de método de pagamento nos modais de despesa e receita
const paymentMethodSelectExpense = addExpenseModal.querySelector("#payment_method");
const paymentMethodSelectIncome = addIncomeModal.querySelector("#payment_method");

// Adicione ouvintes de eventos aos campos de seleção de método de pagamento
paymentMethodSelectExpense.addEventListener("change", () => {
  const selectedPaymentMethod = paymentMethodSelectExpense.value;
  const cashDivExpense = document.getElementById("cash_select_div_expense");
  const bankDivExpense = document.getElementById("bank_select_div_expense");

  cashDivExpense.style.display = selectedPaymentMethod === "cash" ? "block" : "none";
  bankDivExpense.style.display = selectedPaymentMethod === "bank" ? "block" : "none";
});

paymentMethodSelectIncome.addEventListener("change", () => {
  const selectedPaymentMethod = paymentMethodSelectIncome.value;
  const cashDivIncome = document.getElementById("cash_select_div_income");
  const bankDivIncome = document.getElementById("bank_select_div_income");

  cashDivIncome.style.display = selectedPaymentMethod === "cash" ? "block" : "none";
  bankDivIncome.style.display = selectedPaymentMethod === "bank" ? "block" : "none";
});

document.getElementById("filter").addEventListener("change", () => {
  const filter = document.getElementById("filter").value;
  const startDateInput = document.getElementById("start-date");
  const endDateInput = document.getElementById("end-date");

  startDateInput.style.display = filter === "range" ? "block" : "none";
  endDateInput.style.display = filter === "range" ? "block" : "none";

  if (filter === "range") {
    initializeDateInput(startDateInput);
    initializeDateInput(endDateInput);
  }
});

function initializeDateInput(dateInput) {
  flatpickr(dateInput, {
    dateFormat: "Y-m-d",
    minDate: "2000-01-01",
    maxDate: "2099-12-31",
    altInput: true,
    altFormat: "F j, Y",
    allowInput: true,
    clickOpens: true,
  });
}

document.getElementById("filter-button").addEventListener("click", () => {
  const filter = document.getElementById("filter").value;
  const startDate = document.getElementById("start-date").value;
  const endDate = document.getElementById("end-date").value;

  const data = { filter };
  if (filter === "range") {
    data.start_date = startDate;
    data.end_date = endDate;
  }

  fetch("/filter", {
    method: "POST",
    body: JSON.stringify(data),
    headers: {
      "Content-Type": "application/json",
    },
  })
    .then((response) => response.json())
    .then((data) => {
      const tableBody = document.getElementById("data").querySelector("tbody");
      tableBody.innerHTML = "";

      data.transactions.forEach((money) => {
        const row = document.createElement("tr");
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
        location.reload();
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
        location.reload();
      } else {
        console.log("Failed to delete the bank.");
      }
    })
    .catch((error) => {
      console.error("Error:", error);
    });
}
