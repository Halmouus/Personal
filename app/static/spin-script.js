const wheelCanvas = document.getElementById("wheel");
const spinButton = document.getElementById("spin-btn");
const finalResult = document.getElementById("final-value");

const data = [16, 16, 16, 16, 16, 16]; // Evenly distributed sections
const pieColors = ["#8b35bc", "#b163da", "#8b35bc", "#b163da", "#8b35bc", "#b163da"];

let myChart = new Chart(wheelCanvas, {
  type: "pie",
  data: {
    labels: [1, 2, 3, 4, 5, 6],
    datasets: [{
      backgroundColor: pieColors,
      data: data,
    }],
  },
  options: {
    responsive: true,
    animation: { animateRotate: true, duration: 0 },
    plugins: {
      tooltip: { enabled: false },
      legend: { display: false },
      datalabels: {
        color: "#fff",
        font: { size: 20 },
        formatter: (value, ctx) => ctx.chart.data.labels[ctx.dataIndex],
      }
    }
  }
});

spinButton.addEventListener("click", () => {
  const totalDegrees = 3600; // 10 full rotations for dramatic effect
  let currentRotation = Math.floor(Math.random() * 360);
  myChart.options.rotation = Math.degrees * (currentRotation + totalDegrees);
  myChart.update();
  setTimeout(() => {
    const result = determinePrize(currentRotation % 360);
    finalResult.innerHTML = `<p>Your prize number: ${result}</p>`;
  }, 5000); // Show result after 5 seconds
});

function determinePrize(angle) {
  const slices = 6;
  const sliceDegrees = 360 / slices;
  return Math.floor(angle / sliceDegrees) + 1;
}
