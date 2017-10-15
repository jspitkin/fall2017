/** Class implementing the votePercentageChart. */
class VotePercentageChart {

    /**
     * Initializes the svg elements required for this chart;
     */
    constructor(){
	    this.margin = {top: 30, right: 20, bottom: 30, left: 50};
	    let divvotesPercentage = d3.select("#votes-percentage").classed("content", true);

	    //fetch the svg bounds
	    this.svgBounds = divvotesPercentage.node().getBoundingClientRect();
	    this.svgWidth = this.svgBounds.width - this.margin.left - this.margin.right;
	    this.svgHeight = 200;

	    //add the svg to the div
	    this.svg = divvotesPercentage.append("svg")
	        .attr("width",this.svgWidth)
	        .attr("height",this.svgHeight)

    }


	/**
	 * Returns the class that needs to be assigned to an element.
	 *
	 * @param party an ID for the party that is being referred to.
	 */
	chooseClass(data) {
	    if (data == "R"){
	        return "republican";
	    }
	    else if (data == "D"){
	        return "democrat";
	    }
	    else if (data == "I"){
	        return "independent";
	    }
	}

	/**
	 * Renders the HTML content for tool tip
	 *
	 * @param tooltip_data information that needs to be populated in the tool tip
	 * @return text HTML content for toop tip
	 */
	tooltip_render (tooltip_data) {
	    let text = "<ul>";
	    tooltip_data.result.forEach((row)=>{
	        text += "<li class = " + this.chooseClass(row.party)+ ">" + row.nominee+":\t\t"+row.votecount+"("+row.percentage+"%)" + "</li>"
	    });

	    return text;
	}

	/**
	 * Creates the stacked bar chart, text content and tool tips for Vote Percentage chart
	 *
	 * @param electionResult election data for the year selected
	 */
	update (electionResult){
        
		//for reference:https://github.com/Caged/d3-tip
		//Use this tool tip element to handle any hover over the chart
		let tip = d3.tip().attr('class', 'd3-tip')
			.direction('s')
			.offset(function() {
				return [0,0];
			})
			.html((d)=> {
				/* populate data in the following format
					* tooltip_data = {
					* "result":[
					* {"nominee": D_Nominee_prop,"votecount": D_Votes_Total,"percentage": D_PopularPercentage,"party":"D"} ,
					* {"nominee": R_Nominee_prop,"votecount": R_Votes_Total,"percentage": R_PopularPercentage,"party":"R"} ,
					* {"nominee": I_Nominee_prop,"votecount": I_Votes_Total,"percentage": I_PopularPercentage,"party":"I"}
					* ]
					* }
					* pass this as an argument to the tooltip_render function then,
					* return the HTML content returned from that method.
					* */
				return;
			});
	
		// Find the percent for each party
		let dPercent = electionResult[0]['D_PopularPercentage'];
		dPercent = +dPercent.substring(0, dPercent.length - 1);
		let rPercent = electionResult[0]['R_PopularPercentage'];
		rPercent = +rPercent.substring(0, rPercent.length - 1);
		let iPercent = electionResult[0]['I_PopularPercentage'];
		iPercent = +iPercent.substring(0, iPercent.length - 1);
	
		let widthScale = d3.scaleLinear()
			.domain([0, 100])
			.range([0, this.svgWidth]);
		
		let data = [{ 'party' : "I", 'percent' : iPercent},
					{ 'party' : "D", 'percent' : dPercent},
					{ 'party' : "R", 'percent' : rPercent}];

		// Create the stacked bar chart
		const BAR_Y = this.svgHeight / 4;
		const BAR_HEIGHT = this.svgHeight / 4;
		let currentX = 0;
		this.svg.selectAll("rect")
			.data(data)
			.enter()
			.append("rect")
			.attr("x", function(d) {
				currentX += widthScale(d['percent']);
				return currentX - widthScale(d['percent']);
			})
			.attr("y", BAR_Y)
			.attr("height", BAR_HEIGHT)
			.attr("width", d => widthScale(d['percent']))
			.attr("class", d => this.chooseClass(d['party']))
			.classed("votesPercentage", true);
		
		// Add marker to show the middle point
		this.svg.append("rect")
			.attr("x", this.svgWidth / 2)
			.attr("y", BAR_Y - 5)
			.attr("width", 3)
			.attr("height", BAR_HEIGHT + 10)
			.classed("middlePoint", true);
		
		// Add a title for the chart
		this.svg.append("text")
			.attr("x", this.svgWidth * 0.5)
			.attr("y", BAR_Y - 10)
			.text("Popular Vote (50%)")
			.classed("votesPercentageNote", true);

		//Display the total percentage of votes won by each party
		//on top of the corresponding groups of bars.
		//HINT: Use the .votesPercentageText class to style your text elements;  Use this in combination with
		// chooseClass to get a color based on the party wherever necessary

		//Just above this, display the text mentioning details about this mark on top of this bar
		//HINT: Use .votesPercentageNote class to style this text element

		//Call the tool tip on hover over the bars to display stateName, count of electoral votes.
		//then, vote percentage and number of votes won by each party.

		//HINT: Use the chooseClass method to style your elements based on party wherever necessary.

	};


}