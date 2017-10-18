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
	        text += "<li class = " + this.chooseClass(row.party)+ ">" + row.nominee+":\t\t"+row.votecount+" ("+row.percentage+"%)" + "</li>"
	    });

	    return text;
	}

	/**
	 * Creates the stacked bar chart, text content and tool tips for Vote Percentage chart
	 *
	 * @param electionResult election data for the year selected
	 */
	update (electionResult){
		console.log(electionResult);
		//for reference:https://github.com/Caged/d3-tip
		//Use this tool tip element to handle any hover over the chart
		let tip = d3.tip().attr('class', 'd3-tip')
			.direction('s')
			.offset(function() {
				return [0,0];
			})
			.html((d)=> {
				let result = electionResult[0];
				let tooltip_data = {
					'result' : [
						{ 'nominee' 	: result['I_Nominee_prop'],
						  'votecount' 	: result['I_Votes_Total'],
						  'percentage' 	: result['I_PopularPercentage'],
						  'party' 		: "I" },

						{ 'nominee' 	: result['D_Nominee_prop'],
						  'votecount' 	: result['D_Votes_Total'],
						  'percentage' 	: result['D_PopularPercentage'],
						  'party' 		: "D" },

						{ 'nominee' 	: result['R_Nominee_prop'],
						  'votecount' 	: result['R_Votes_Total'],
						  'percentage' 	: result['R_PopularPercentage'],
						  'party' 		: "R" }
					]
				};

				// Remove ind if no votes
				if (result['I_PopularPercentage'] == 0) {
					tooltip_data['result'] = tooltip_data['result'].slice(1);
				}

				return this.tooltip_render(tooltip_data);
			});
		
		// Remove old elements
		this.svg.selectAll("rect").remove();
		this.svg.selectAll("text").remove();
	
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
		const BAR_Y = this.svgHeight * 0.6;
		const BAR_HEIGHT = this.svgHeight / 4;
		let currentX = 0;
		let stackedBar = this.svg.selectAll("rect")
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
		
		// Add a tooltip when hoving on the stacked bar chart
		stackedBar.call(tip);
		stackedBar.on("mouseover", tip.show);
		stackedBar.on("mouseout", tip.hide);
		
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
		
		// Add percentage for ind votes (if any)
		if (iPercent > 0) {
			this.svg.append("text")
				.attr("x", 0)
				.attr("y", BAR_Y - 10)
				.text(electionResult[0]['I_PopularPercentage'])
				.classed("votesPercentageText", true)
				.classed(this.chooseClass("I"), true);
		}

		// Add percentage for dem votes
		this.svg.append("text")
			.attr("x", function() {
				if (iPercent > 0) {
					return widthScale(iPercent) + 70;
				}
				return widthScale(iPercent);
			})
			.attr("y", BAR_Y - 10)
			.text(electionResult[0]['D_PopularPercentage'])
			.classed("votesPercentageText", true)
			.classed(this.chooseClass("D"), true);
		
		// Add percentage for rep votes
		this.svg.append("text")
			.attr("x", this.svgWidth)
			.attr("y", BAR_Y - 10)
			.text(electionResult[0]['R_PopularPercentage'])
			.classed("votesPercentageText", true)
			.classed(this.chooseClass("R"), true);
		
		// Add ind candidate (if any)
		if (iPercent > 0) {
			this.svg.append("text")
				.attr("x", 30)
				.attr("y", BAR_Y - 80)
				.text(electionResult[0]['I_Nominee_prop'])
				.classed("votesPercentageText", true)
				.classed(this.chooseClass("I"), true);
		}

		// Add dem candidate
		this.svg.append("text")
			.attr("x", function() {
				if (iPercent > 0) {
					return (this.svgWidth / 3.5);
				}
				return 30;
			}.bind(this))
			.attr("y", BAR_Y - 80)
			.text(electionResult[0]['D_Nominee_prop'])
			.classed("votesPercentageText", true)
			.classed(this.chooseClass("D"), true);
		
		// Add rep candidate
		this.svg.append("text")
			.attr("x", this.svgWidth)
			.attr("y", BAR_Y - 80)
			.text(electionResult[0]['R_Nominee_prop'])
			.classed("votesPercentageText", true)
			.classed(this.chooseClass("R"), true);
	};


}