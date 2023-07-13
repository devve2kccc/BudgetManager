document.addEventListener('DOMContentLoaded', () => {
  const cryptoInput = document.getElementById('cryptoInput');
  const cryptoDropdown = document.getElementById('cryptoDropdown');
  const cryptoSymbolInput = document.getElementById('cryptoSymbol');
  const cryptoPriceInput = document.getElementById('cryptoPrice');
  let cryptocurrencies = [];

  fetch('/api/cryptos')
    .then(response => response.json())
    .then(data => {
      cryptocurrencies = data.data;
    })
    .catch(error => {
      console.error(error);
      // Error handling
    })
    .finally(() => {
      cryptoInput.addEventListener('input', handleCryptoInput);
    });

  function handleCryptoInput() {
    const cryptoName = cryptoInput.value.trim();

    let matchingCryptos = [];
    if (cryptoName) {
      matchingCryptos = cryptocurrencies.filter(crypto =>
        crypto.name.toLowerCase().includes(cryptoName.toLowerCase()) ||
        crypto.symbol.toLowerCase().includes(cryptoName.toLowerCase())
      );
    }

    cryptoDropdown.innerHTML = '';

    const suggestionsCount = matchingCryptos.length > 10 ? 10 : matchingCryptos.length;
    for (let i = 0; i < suggestionsCount; i++) {
      const suggestionItem = document.createElement('div');
      suggestionItem.classList.add('dropdown-item');
      suggestionItem.textContent = `${matchingCryptos[i].name} (${matchingCryptos[i].symbol})`;
      suggestionItem.addEventListener('click', () => {
        cryptoInput.value = `${matchingCryptos[i].name} (${matchingCryptos[i].symbol})`;
        cryptoSymbolInput.value = matchingCryptos[i].symbol;
        cryptoPriceInput.value = matchingCryptos[i].quote.USD.price.toFixed(2);
        document.getElementById('cryptoId').value = matchingCryptos[i].id;
        cryptoDropdown.classList.remove('show'); // Close the dropdown
      });

      cryptoDropdown.appendChild(suggestionItem);
    }

    if (matchingCryptos.length === 0) {
      const noResultsItem = document.createElement('div');
      noResultsItem.classList.add('dropdown-item', 'disabled');
      noResultsItem.textContent = 'No results found';

      cryptoDropdown.appendChild(noResultsItem);
    }

    cryptoDropdown.classList.add('show');
  }

  // Close the dropdown when clicking outside
  document.addEventListener('click', (event) => {
    if (!cryptoDropdown.contains(event.target)) {
      cryptoDropdown.classList.remove('show');
    }
  });
});
