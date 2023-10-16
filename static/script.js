// Sample data
const data = [10, 30, 45, 60, 80];

// Set up the chart dimensions
const width = 400;
const height = 300;
const barWidth = 40;

// Create an SVG element to contain the chart
const svg = d3.select("#chart-container")
    .append("svg")
    .attr("width", width)
    .attr("height", height);

// Create the bars
svg.selectAll("rect")
    .data(data)
    .enter()
    .append("rect")
    .attr("x", (d, i) => i * (barWidth + 10))
    .attr("y", d => height - d)
    .attr("width", barWidth)
    .attr("height", d => d)
    .attr("fill", "blue");

// You can also add labels, axes, and other features here