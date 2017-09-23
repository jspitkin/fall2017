/** Class implementing the bar chart view. */
class BarChart {

    /**
     * Create a bar chart instance and pass the other views in.
     * @param worldMap
     * @param infoPanel
     * @param allData
     */
    constructor(worldMap, infoPanel, allData) {
        this.worldMap = worldMap;
        this.infoPanel = infoPanel;
        this.allData = allData;
    }

    /**
     * Render and update the bar chart based on the selection of the data type in the drop-down box
     */
    updateBarChart(selectedDimension) {
        // Select data and years for updated bar chart
        let selectedData = this.allData.map(d => d[selectedDimension]).reverse();
        this.yearData = this.allData.map(d => +d['YEAR']).reverse();
        this.barChart = d3.select("#barChart");
        this.currentWorldCup = null;

        // Styling and positions for bar chart
        let barWidth = 18;
        let padding = 10;
        let yAxisWidth = 60;
        let xAxisHeight = 60;
        let yAxisHeight = this.barChart.attr("height") - xAxisHeight;
        let xAxisYPos = this.barChart.attr("height") - xAxisHeight;
        let barSpacing = (this.barChart.attr("width") - yAxisWidth - padding - 9) / selectedData.length;
        let transitionTime = 1200;
        
        // Create y-axis
        let yAxisScale = d3.scaleLinear()
            .domain([d3.max(selectedData), 0])
            .range([0, (this.barChart.attr("height") - (xAxisHeight + 12))])
            .nice();
        let yAxis = d3.axisLeft(yAxisScale);
        d3.select("#yAxis")
            .attr("transform", function() {
                return "translate(" + (yAxisWidth+padding) + "," + padding + ")";
            })
            .transition()
            .duration(transitionTime*2)
            .call(yAxis);

        
        // Create x-axis
        let xAxisScale = d3.scaleLinear()
            .domain([0, this.yearData.length])
            .range([0, this.barChart.attr("width") - (yAxisWidth + padding + padding - 2)]);
        let xAxis = d3.axisBottom(xAxisScale);
        xAxis.ticks(this.yearData.length);
        d3.select("#xAxis")
            .attr("transform", function() {
                return "translate(" + (yAxisWidth+padding+barWidth) + "," + xAxisYPos + ")";
            })
            .call(xAxis)
            .selectAll("text")
            .text(function(d,i) {
                return this.yearData[i];
            }.bind(this))
            .attr("y", 0)
            .attr("x", 10)
            .attr("dy", 5)
            .attr("transform", "rotate(90)")
            .style("text-anchor", "start");

        // Scales for bar chart
        let yScale = d3.scaleLinear()
            .domain([0, d3.max(selectedData)])
            .range([0, this.barChart.attr("height") - (xAxisHeight + 12)])
        let colorScale = d3.scaleLinear()
            .domain([d3.min(selectedData), d3.max(selectedData)])
            .range(["lightsteelblue", "steelblue", "darksteelblue"]);
        

        // Create bars of bar chart
        let bars = this.barChart.select("#bars")
            .selectAll(".bars")
            .data(selectedData)

        bars.exit().remove();

        bars = bars.enter().append("rect").merge(bars);

        // Position and scale the bars
        bars.transition()
            .duration(transitionTime)
            .attr("height", function(d) {
                return yScale(d);
            })
            .style("fill", function(d) {
                return colorScale(d);
            });

        bars.attr("x", function(d, i) {
                return (i * barSpacing);
            })
           .attr("y", 0)
           .attr("width", function(d, i) {
               return barWidth;
            })
            .attr("id", function(d, i) {
                return this.yearData[i];
            }.bind(this))
            .classed("bars", true);

        
        // Transform and scale the chart
        this.barChart.select("#bars")
            .attr("transform", function() {
                return "translate(" + (yAxisWidth+padding*2) + "," + (xAxisYPos)+ ") scale(1, -1)";
            })

        // ******* TODO: PART II *******
        this.barChart.selectAll(".bars")
            .on('click', function() {
                this.barChart.selectAll(".bars")
                    .style("fill", function(d) {
                        return colorScale(d);
                    })     
                d3.event.target.style.fill = "red";
                let worldCupYear = d3.event.target.id;
                let worldCup = this.allData.filter(d => d['YEAR'] == worldCupYear)[0];
                this.infoPanel.updateInfo(worldCup);
                this.worldMap.updateMap(worldCup);
            }.bind(this));
    }

    /**
     *  Check the drop-down box for the currently selected data type and update the bar chart accordingly.
     *
     *  There are 4 attributes that can be selected:
     *  goals, matches, attendance and teams.
     */
    chooseData() {
        // ******* TODO: PART I *******
        //Changed the selected data when a user selects a different
        // menu item from the drop down.

    }
}