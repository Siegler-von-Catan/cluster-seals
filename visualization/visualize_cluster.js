// ClusterSeals - Transform seal dataset for visualization
// Copyright (C) 2021
// Joana Bergsiek, Leonard Geier, Lisa Ihde,
// Tobias Markus, Dominik Meier, Paul Methfessel
//
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with this program.  If not, see <https://www.gnu.org/licenses/>.

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

  const dots = d3.select("#seals")
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
  
  const clusters = await d3.csv("cluster_seals.csv", ({cluster, desc}) => {
    return {
      cluster: Number(cluster),
      desc,
    }
  });
  console.log(clusters);

  d3.select("#labels")
    .selectAll("g")
    .data(clusters)
    .enter()
    .append("g")
      .attr("transform", (d, i) => `translate(10 ${15 + i * 15})`)
    .append("text")
      .attr("fill", d => color(d.cluster))
      .text(d => d.desc.replace(/\./g, " ").replace(/(Krone|Wappenschild|Helm)/g, ""));
})();
