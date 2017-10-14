
class YearChart {

    /**
     * Constructor for the Year Chart
     *
     * @param electoralVoteChart instance of ElectoralVoteChart
     * @param tileChart instance of TileChart
     * @param votePercentageChart instance of Vote Percentage Chart
     * @param electionInfo instance of ElectionInfo
     * @param electionWinners data corresponding to the winning parties over mutiple election years
     */
    constructor (electoralVoteChart, tileChart, votePercentageChart, electionWinners) {

        //Creating YearChart instance
        this.electoralVoteChart = electoralVoteChart;
        this.tileChart = tileChart;
        this.votePercentageChart = votePercentageChart;
        // the data
        this.electionWinners = electionWinners;
        
        // Initializes the svg elements required for this chart
        this.margin = {top: 10, right: 20, bottom: 30, left: 50};
        let divyearChart = d3.select("#year-chart").classed("fullView", true);

        //fetch the svg bounds
        this.svgBounds = divyearChart.node().getBoundingClientRect();
        this.svgWidth = this.svgBounds.width - this.margin.left - this.margin.right;
        this.svgHeight = 100;

        //add the svg to the div
        this.svg = divyearChart.append("svg")
            .attr("width", this.svgWidth)
            .attr("height", this.svgHeight)
    };


    /**
     * Returns the class that needs to be assigned to an element.
     *
     * @param party an ID for the party that is being referred to.
     */
    chooseClass (data) {
        if (data == "R") {
            return "yearChart republican";
        }
        else if (data == "D") {
            return "yearChart democrat";
        }
        else if (data == "I") {
            return "yearChart independent";
        }
    }

    /**
     * Creates a chart with circles representing each election year, populates text content and other required elements for the Year Chart
     */
    update () {
        const PADDING = 50;
        const DEFAULT_CIRCLE_RADIUS = 14;

        // Domain definition for global color scale
        let domain = [-60, -50, -40, -30, -20, -10, 0, 10, 20, 30, 40, 50, 60];

        //Color range for global color scale
        let range = ["#063e78", "#08519c", "#3182bd", "#6baed6", "#9ecae1", "#c6dbef", "#fcbba1", "#fc9272", "#fb6a4a", "#de2d26", "#a50f15", "#860308"];

        // Global colorScale be used consistently by all the charts
        this.colorScale = d3.scaleQuantile()
            .domain(domain)
            .range(range);
        
        // X scale for circles
        let xScale = d3.scaleLinear()
            .domain([0, this.electionWinners.length - 1])
            .range([PADDING, this.svgWidth - PADDING]);

        // append dashed line behind circles
        this.svg.insert("line")
            .attr("x1", 0)
            .attr("y1", this.svgHeight / 3)
            .attr("x2", this.svgWidth)
            .attr("y2", this.svgHeight / 3)
            .classed("lineChart", true);

        // append circles
        this.svg.selectAll("circle")
            .data(this.electionWinners)
            .enter()
            .append("circle")
            .attr("cx", (d, i) => xScale(i))
            .attr("cy", this.svgHeight / 3)
            .attr("r", DEFAULT_CIRCLE_RADIUS)
            .attr("class", d => this.chooseClass(d['PARTY']));

        // append text labels
        this.svg.selectAll("text")
            .data(this.electionWinners)
            .enter()
            .append("text")
            .attr("x", (d, i) => xScale(i))
            .attr("y", this.svgHeight * 0.8)
            .text(d => d['YEAR'])
            .classed("yeartext", true);

        // hover and click event handlers
        this.svg.selectAll("circle")
            .on("mouseenter", function(d) {
                d3.select(this).classed("highlighted", true);
            })
            .on("mouseleave", function(d) {
                d3.select(this).classed("highlighted", false);
            })
            .on("click", function(d) {
                let csvPath = "data/Year_Timeline_" + d['YEAR'] + ".csv";
                d3.csv(csvPath, function(error, yearData) {
                    this.electoralVoteChart.update(yearData, this.colorScale);
                    this.tileChart.update(yearData, this.colorScale);
                    this.votePercentageChart.update(yearData);
                }.bind(this));
            }.bind(this));

    //******* TODO: EXTRA CREDIT *******

    //Implement brush on the year chart created above.
    //Implement a call back method to handle the brush end event.
    //Call the update method of shiftChart and pass the data corresponding to brush selection.
    //HINT: Use the .brush class to style the brush.

    };

};