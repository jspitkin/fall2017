/** Class implementing the tileChart. */
class TileChart {

    /**
     * Initializes the svg elements required to lay the tiles
     * and to populate the legend.
     */
    constructor(){

        let divTiles = d3.select("#tiles").classed("content", true);
        this.margin = {top: 30, right: 20, bottom: 30, left: 50};
        //Gets access to the div element created for this chart and legend element from HTML
        let svgBounds = divTiles.node().getBoundingClientRect();
        this.svgWidth = svgBounds.width - this.margin.left - this.margin.right;
        this.svgHeight = this.svgWidth/2;
        let legendHeight = 150;
        //add the svg to the div
        let legend = d3.select("#legend").classed("content",true);

        //creates svg elements within the div
        this.legendSvg = legend.append("svg")
                            .attr("width",this.svgWidth)
                            .attr("height",legendHeight)
                            .attr("transform", "translate(" + this.margin.left + ",0)")
                            .style("bgcolor","green")
        this.svg = divTiles.append("svg")
                            .attr("width",this.svgWidth)
                            .attr("height",this.svgHeight)
                            .attr("transform", "translate(" + this.margin.left + ",0)")
                            .style("bgcolor","green")
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
        else if (party== "D"){
            return "democrat";
        }
        else if (party == "I"){
            return "independent";
        }
    }

    /**
     * Renders the HTML content for tool tip.
     *
     * @param tooltip_data information that needs to be populated in the tool tip
     * @return text HTML content for tool tip
     */
    tooltip_render(tooltip_data) {
        let text = "<h2 class ="  + this.chooseClass(tooltip_data.winner) + " >" + tooltip_data.state + "</h2>";
        text +=  "Electoral Votes: " + tooltip_data.electoralVotes;
        text += "<ul>"
        tooltip_data.result.forEach((row)=>{
            //text += "<li>" + row.nominee+":\t\t"+row.votecount+"("+row.percentage+"%)" + "</li>"
            text += "<li class = " + this.chooseClass(row.party)+ ">" + row.nominee+":\t\t"+row.votecount+"("+row.percentage+"%)" + "</li>"
        });
        text += "</ul>";

        return text;
    }

    /**
     * Creates tiles and tool tip for each state, legend for encoding the color scale information.
     *
     * @param electionResult election data for the year selected
     * @param colorScale global quantile scale based on the winning margin between republicans and democrats
     */
    update (electionResult, colorScale){
        //Calculates the maximum number of columns to be laid out on the svg
        this.maxColumns = d3.max(electionResult,function(d){
                                return parseInt(d["Space"]);
                            });

        //Calculates the maximum number of rows to be laid out on the svg
        this.maxRows = d3.max(electionResult,function(d){
                                return parseInt(d["Row"]);
                        });
                        
        //Creates a legend element and assigns a scale that needs to be visualized
        this.legendSvg.append("g")
            .attr("class", "legendQuantile")
            .attr("transform", "translate(125,50)");

        let legendQuantile = d3.legendColor()
            .shapeWidth(120)
            .cells(10)
            .orient('horizontal')
            .scale(colorScale);

        this.legendSvg.select(".legendQuantile")
            .call(legendQuantile);

        //for reference:https://github.com/Caged/d3-tip
        //Use this tool tip element to handle any hover over the chart
        let tip = d3.tip().attr('class', 'd3-tip')
        .direction('se')
        .offset(function() {
            return [0,0];
        })
        .html((d)=> {
            let tooltip_data = {
                'state'  : d['State'],
                'winner' : d['State_Winner'],
                'electoralVotes' : d['Total_EV'],
                'result' : [
                    { 'nominee' 	: d['D_Nominee_prop'],
                      'votecount' 	: d['D_Votes'],
                      'percentage' 	: d['D_Percentage'],
                      'party' 		: "D" },

                    { 'nominee' 	: d['R_Nominee_prop'],
                      'votecount' 	: d['R_Votes'],
                      'percentage' 	: d['R_Percentage'],
                      'party' 		: "R" },

                    { 'nominee' 	: d['I_Nominee_prop'],
                      'votecount' 	: d['I_Votes'],
                      'percentage' 	: d['I_Percentage'],
                      'party' 		: "I" }
                ]
            };

            // Remove ind if no votes
            if (d['I_Percentage'] == 0) {
                tooltip_data['result'].splice(2, 1);
            }

            return this.tooltip_render(tooltip_data);
        });

        const STATE_WIDTH = this.svgWidth / (this.maxColumns + 1);
        const STATE_HEIGHT = this.svgHeight / (this.maxRows + 1);
        
        let xScale = d3.scaleLinear()
            .domain([0, this.maxColumns])
            .range([0, this.svgWidth - STATE_WIDTH]);

        let yScale = d3.scaleLinear()
            .domain([0, this.maxRows])
            .range([0, this.svgHeight - STATE_HEIGHT]);

        // Create each tile
        let tiles = this.svg.selectAll("rect").data(electionResult);
        tiles = tiles.enter().append("rect").merge(tiles);

        // Add coloring
        tiles.attr("x", d => xScale(+d["Space"]))
            .attr("y", d => yScale(+d["Row"]))
            .attr("width", STATE_WIDTH)
            .attr("height", STATE_HEIGHT)
            .style("fill", function(d) {
                return d['State_Winner'] == "I" ? "#01A142" : colorScale(d['RD_Difference']);
            })
            .classed("tile", true);

        // Add state abbreviation to each state
        let stateAbbr = this.svg.selectAll("text.abbr").data(electionResult);
        stateAbbr = stateAbbr.enter().append("text").merge(stateAbbr);
        stateAbbr.attr("x", d => xScale(+d["Space"]) + STATE_WIDTH / 2)
            .attr("y", d => yScale(+d["Row"]) + STATE_HEIGHT / 2.3)
            .text(function(d) {
                return d['Abbreviation'];
            })
            .classed("tilestext", true)
            .classed("abbr", true);
        
        // Add state electoral votes to each state
        let stateVotes = this.svg.selectAll("text.votes").data(electionResult);
        stateVotes = stateVotes.enter().append("text").merge(stateVotes);
        stateVotes.attr("x", d => xScale(+d["Space"]) + STATE_WIDTH / 2)
            .attr("y", d => yScale(+d["Row"]) + STATE_HEIGHT / 1.3)
            .text(function(d) {
                return d['Total_EV'];
            })
            .classed("tilestext", true)
            .classed("votes", true);
            
        // Add tooltip on hover to each state
        tiles.call(tip)
		tiles.on("mouseover", tip.show);
		tiles.on("mouseout", tip.hide);
    };

}
