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



        // ******* TODO: PART I *******
        let selectedData = this.allData.map(d => d[selectedDimension]);
        let yearData = this.allData.map(d => +d['YEAR']).reverse();
        let barChart = d3.select("#barChart");
        let colorScale = d3.scaleLinear()
            .domain([d3.min(selectedData), d3.max(selectedData)])
            .range(["lightsteelblue", "steelblue", "darksteelblue"]);
        let barWidth = 20;
        let padding = 10;
        let yAxisWidth = 60;
        let xAxisHeight = 60;
        let yAxisHeight = barChart.attr("height") - xAxisHeight;
        let xAxisYPos = barChart.attr("height") - xAxisHeight;
        let barSpacing = (barChart.attr("width") - yAxisWidth) / selectedData.length;


        //let bars = barChart.select('#bars')
          //  .selectAll('.bars')
            //.data(this.allData);

//        bars.exit().remove();

//        bars = bars.enter().append('rect').classed('.bars', true).merge(bars);

//        bars.attr('height', function(d) {
    //            return yScale(d[selectedDimension]);
  //          })
      //      .attr('x', function(d, i) {
       //         return (i * barSpacing);
        //    })
         //   .attr('y', 0)
          //  .attr('width', function(d, i) {
          //      return barWidth;
          //  })
          //  .style('fill', function(d) {
          //      return colorScale(d[selectedDimension]);
          //  });
        
        // Create y-axis
        let yAxisScale = d3.scaleLinear()
            .domain([d3.max(selectedData), 0])
            .range([0, (barChart.attr("height") - (xAxisHeight + 12))])
            .nice();
        let yAxis = d3.axisLeft(yAxisScale);
        d3.select("#yAxis")
            .attr("transform", "translate(" + (yAxisWidth+padding) + "," + padding + ")")
            .call(yAxis);

        // Create x-axis
        let xAxisScale = d3.scaleLinear()
            .domain([0, yearData.length])
            .range([padding, barChart.attr("width") - (yAxisWidth + padding)]);
        let xAxis = d3.axisBottom(xAxisScale);
        xAxis.ticks(yearData.length);
        d3.select("#xAxis")
            .attr("transform", function() {
                return "translate(" + (yAxisWidth+padding) + "," + xAxisYPos + ")";
            })
            .call(xAxis)
            .selectAll("text")
            .text(function(d,i) {
                return yearData[i];
            })
            .attr("y", 0)
            .attr("x", 10)
            .attr("dy", 5)
            .attr("transform", "rotate(90)")
            .style("text-anchor", "start");
        

        // Create the x and y scales; make
        // sure to leave room for the axes

        // Create colorScale

        // Create the axes (hint: use #xAxis and #yAxis)

        // Create the bars (hint: use #bars)




        // ******* TODO: PART II *******

        // Implement how the bars respond to click events
        // Color the selected bar to indicate is has been selected.
        // Make sure only the selected bar has this new color.

        // Call the necessary update functions for when a user clicks on a bar.
        // Note: think about what you want to update when a different bar is selected.

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