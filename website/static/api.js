document.addEventListener('DOMContentLoaded', () => {
    const cryptoNameInput = document.getElementById('cryptoName');
    const cryptoDropdown = document.getElementById('cryptoDropdown');
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
        cryptoNameInput.addEventListener('keyup', handleCryptoInput);
      });
  
    function handleCryptoInput() {
      const cryptoName = cryptoNameInput.value;
  
      let matchingCryptos = [];
      if (cryptoName) {
        matchingCryptos = cryptocurrencies.filter(crypto =>
          crypto.name.toLowerCase().startsWith(cryptoName.toLowerCase()) ||
          crypto.symbol.toLowerCase().startsWith(cryptoName.toLowerCase())
        );
      }
  
      cryptoDropdown.innerHTML = '';
  
      const suggestionsCount = matchingCryptos.length > 10 ? 10 : matchingCryptos.length;
      for (let i = 0; i < suggestionsCount; i++) {
        const suggestionItem = document.createElement('div');
        suggestionItem.classList.add('dropdown-item');
        suggestionItem.textContent = `${matchingCryptos[i].name} (${matchingCryptos[i].symbol})`;
        suggestionItem.addEventListener('click', () => {
          cryptoNameInput.value = `${matchingCryptos[i].name} (${matchingCryptos[i].symbol})`;
          cryptoDropdown.innerHTML = '';
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
  });
  