document.addEventListener('DOMContentLoaded', () => {
    const cryptoNameInput = document.getElementById('cryptoName');
    cryptoNameInput.addEventListener('input', handleCryptoInput);
  });
  
  function handleCryptoInput() {
    const cryptoNameInput = document.getElementById('cryptoName');
    const cryptoName = cryptoNameInput.value;
  
    const proxyUrl = 'https://cors-anywhere.herokuapp.com/';
    const apiUrl = `https://api.coinmarketcap.com/v2/ticker/?limit=100`;
  
    fetch(proxyUrl + apiUrl)
      .then(response => response.json())
      .then(data => {
        const cryptocurrencies = Object.values(data.data);
        const matchingCryptos = cryptocurrencies.filter(crypto =>
          crypto.name.toLowerCase().includes(cryptoName.toLowerCase()) ||
          crypto.symbol.toLowerCase().includes(cryptoName.toLowerCase())
        );
  
        const cryptoList = document.getElementById('cryptoList');
        cryptoList.innerHTML = '';
  
        matchingCryptos.forEach(crypto => {
          const listItem = document.createElement('li');
          listItem.textContent = `${crypto.name} (${crypto.symbol})`;
          listItem.addEventListener('click', () => {
            document.getElementById('cryptoName').value = crypto.name;
            document.getElementById('cryptoId').value = crypto.id;
            document.getElementById('cryptoSymbol').value = crypto.symbol;
            cryptoList.innerHTML = '';
          });
  
          cryptoList.appendChild(listItem);
        });
      })
      .catch(error => {
        console.error(error);
        // Error handling
      });
  }
  