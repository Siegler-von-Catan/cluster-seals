(async () => {

  const coords = await d3.csv("seals.csv", ({id, cluster, x, y}) => {
    return {
      id: Number(id),
      cluster: Number(cluster),
      x: Number(x),
      y: Number(y),
    }
  });

  let subset = coords;
  const extentX = d3.extent(subset.map(row => row.x));
  const extentY = d3.extent(subset.map(row => row.y));

  const scaleX = d3.scaleLinear().domain(extentX).range([0, 500]);
  const scaleY = d3.scaleLinear().domain(extentY).range([0, 500]);

  const dots = d3.select("svg")
    .selectAll("g")
    .data(subset)
    .enter()
    .append("g")
    .attr("transform", d => `translate(${scaleX(d.x)} ${scaleY(d.y)})`);

  const color = d3.scaleOrdinal(d3.schemeCategory10);
  console.log(color);

  dots.append("circle")
      // .attr("cx", d => d.x * 500)
      // .attr("cy", d => d.y * 500)
      .attr("fill", d => color(d.cluster))
      .attr("r", 2);

  // dots.append("text")
  //     .text(d => d.id);
})();
