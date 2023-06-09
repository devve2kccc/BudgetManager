document.addEventListener("DOMContentLoaded", function () {
  fetch("/api/chart-data")
    .then((response) => response.json())
    .then((data) => {
      var ctx = document.getElementById("bankChart").getContext("2d");
      var myChart = new Chart(ctx, {
        type: "doughnut",
        data: data,
        options: {
          responsive: true,
          maintainAspectRatio: false,
          borderWidth: 0,
          legend: {
            display: false, // Set the legend position to 'right'
          },
        },
      });
    })
    .catch((error) => console.error("Error:", error));
});


document.addEventListener("DOMContentLoaded", function () {
  fetch("/api/total-money")
    .then((response) => response.json())
    .then((data) => {
      // Extract the totalMoney value from the response data
      const totalMoney = data.totalMoney;

      // Prepare the data for the chart (same as before)
      const chartData = {
        labels: ["Cash", "Banks"],
        datasets: [
          {
            data: [data.cash, data.bankTotal],
            backgroundColor: ['#FF6384', '#36A2EB', '#FFCE56', '#8A2BE2', '#3CB371', '#BA55D3', '#FF4500', '#9932CC', '#FFA500', '#00CED1'],
          },
        ],
      };

      // Configure the chart (same as before)
      const chartOptions = {
        responsive: true,
        maintainAspectRatio: false,
        borderWidth: 0,
      };

      // Get the chart canvas element (same as before)
      const ctx = document.getElementById("totalMoneyChart").getContext("2d");

      // Create the Doughnut chart (same as before)
      const myChart = new Chart(ctx, {
        type: "doughnut",
        data: chartData,
        options: chartOptions,
      });

      // Display the total money in the chart
      const chartCenter = myChart.chartArea.center;
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";
      ctx.font = "bold 20px Arial";
      ctx.fillText(
        "Total: $" + totalMoney.toFixed(2),
        chartCenter.x,
        chartCenter.y
      );
    })
    .catch((error) => console.error("Error:", error));
});
