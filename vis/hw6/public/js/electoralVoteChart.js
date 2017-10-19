   
class ElectoralVoteChart {
    /**
     * Constructor for the ElectoralVoteChart
     *
     * @param shiftChart an instance of the ShiftChart class
     */
    constructor (shiftChart){
        this.shiftChart = shiftChart;
        
        this.margin = {top: 30, right: 20, bottom: 30, left: 50};
        let divelectoralVotes = d3.select("#electoral-vote").classed("content", true);

        //Gets access to the div element created for this chart from HTML
        this.svgBounds = divelectoralVotes.node().getBoundingClientRect();
        this.svgWidth = this.svgBounds.width - this.margin.left - this.margin.right;
        this.svgHeight = 150;

        //creates svg element within the div
        this.svg = divelectoralVotes.append("svg")
            .attr("width",this.svgWidth)
            .attr("height",this.svgHeight)
    };

    /**
     * Returns the class that needs to be assigned to an element.
     *
     * @param party an ID for the party that is being referred to.
     */
    chooseClass (party) {
        if (party == "R"){
            return "republican";
        }
        else if (party == "D"){
            return "democrat";
        }
        else if (party == "I"){
            return "independent";
        }
    }

    /**
     * Creates the stacked bar chart, text content and tool tips for electoral vote chart
     *
     * @param electionResult election data for the year selected
     * @param colorScale global quantile scale based on the winning margin between republicans and democrats
     */
    update (electionResult, colorScale){
        // Remove existing elements
        this.svg.selectAll("rect").remove();
        this.svg.selectAll("text").remove();

        // Group the states based on the winning party for the state
        let dStates = electionResult.filter(d => d['State_Winner'] == "D");
        let rStates = electionResult.filter(d => d['State_Winner'] == "R");
        let iStates = electionResult.filter(d => d['State_Winner'] == "I");

        // Sort the states based on margin of victory
        dStates.sort((a, b) => a['RD_Difference'] - b['RD_Difference']);
        rStates.sort((a, b) => a['RD_Difference'] - b['RD_Difference']);

        // Concatenate sorted states
        let sortedElectionResult = iStates.concat(dStates).concat(rStates);

        // Create a width scale
        const D_EV_TOTAL = +electionResult[0]['D_EV_Total'];
        const R_EV_TOTAL = +electionResult[0]['R_EV_Total'];
        const I_EV_TOTAL = +electionResult[0]['I_EV_Total']
        const EV_TOTAL = D_EV_TOTAL + R_EV_TOTAL + I_EV_TOTAL;
        let widthScale = d3.scaleLinear()
            .domain([0, EV_TOTAL])
            .range([0, this.svgWidth]);

        //Create the stacked bar chart
        const BAR_Y = this.svgHeight / 2;
        const BAR_HEIGHT = this.svgHeight / 4;
        let currentX = 0;
        this.svg.selectAll("rect")
            .data(sortedElectionResult)
            .enter()
            .append("rect")
            .attr("x", function(d) {
                currentX += widthScale(d['Total_EV']);
                return currentX - widthScale(d['Total_EV']);
            })
            .attr("y", BAR_Y)
            .attr("height", BAR_HEIGHT) 
            .attr("width", d => widthScale(d['Total_EV']))
            .style("fill", function(d) {
                return d['State_Winner'] == "I" ? "#01A142" : colorScale(d['RD_Difference']);
            })
            .classed("electoralVotes", true);
    
        // Add label for independent votes (if any)
        if (I_EV_TOTAL > 0) {
            this.svg.append("text")
                .attr("x", 0)
                .attr("y", BAR_Y - 10)
                .text(I_EV_TOTAL)
                .classed("electoralVoteText", true)
                .classed(this.chooseClass("I"), true);
        }
    
        // Add label for dem votes
        let firstDemXPos = this.svg.selectAll("rect")
            .filter( (d, i) => i == iStates.length).attr("x");
        this.svg.append("text")
            .attr("x", firstDemXPos)
            .attr("y", BAR_Y - 10)
            .text(D_EV_TOTAL)
            .classed("electoralVoteText", true)
            .classed(this.chooseClass("D"), true);
   
        // Add label for rep votes
        let firstRepXPos = this.svg.selectAll("rect")
            .filter( (d, i) => i == sortedElectionResult.length - 1).attr("x");
        this.svg.append("text")
            .attr("x", this.svgWidth)
            .attr("y", BAR_Y - 10)
            .text(R_EV_TOTAL)
            .classed("electoralVoteText", true)
            .classed(this.chooseClass("R"), true);

        // Add marker to show the middle point
        this.svg.append("rect")
            .attr("x", this.svgWidth / 2)
            .attr("y", BAR_Y - 5)
            .attr("width", 3)
            .attr("height", BAR_HEIGHT + 10)
            .classed("middlePoint", true);
    
        // Add a title for the chart
        let neededVotes = Math.floor(EV_TOTAL / 2) + 1;
        this.svg.append("text")
            .attr("x", this.svgWidth * 0.39)
            .attr("y", BAR_Y - 10)
            .text("Electoral Vote (" +neededVotes + " needed to win)")
            .classed("electoralVoteNote", true);

        // Create the brush with the bounds of the electoral vote chart
        let brush = d3.brushX()
            .extent([[0, BAR_Y], [this.svgWidth, BAR_Y + BAR_HEIGHT]])
            .on("end", function(d) {
                // Bounds for the brush
                let lowerBound = d3.event.selection[0];
                let upperBound = d3.event.selection[1];
                let selectedStates = [];
                let currentX = 0;
                // Consider each state and see if the state is in bounds of the brush
                for (let i = 0; i < sortedElectionResult.length; i++) {
                    let xUpdate = widthScale(sortedElectionResult[i]['Total_EV']);
                    if (currentX >= lowerBound && currentX + xUpdate <= upperBound) {
                        selectedStates.push(sortedElectionResult[i]);
                    }
                    // Update the current position in the bar chart
                    currentX += xUpdate;
                }
                // Pass the selected states to the shift chart
                this.shiftChart.update(selectedStates);
            }.bind(this));

        // Add the brush to the stacked bar chart
        this.svg.append("g").attr("class", "brush").call(brush);
    };

}
