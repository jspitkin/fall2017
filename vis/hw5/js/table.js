/** Class implementing the table. */
class Table {

    /**
     * Creates a Table Object
     */
    constructor(teamData, treeObject) {

        //Maintain reference to the tree Object; 
        this.tree = treeObject; 

        // Create list of all elements that will populate the table
        // Initially, the tableElements will be identical to the teamData
        this.tableElements = teamData.slice(); // 

        ///** Store all match data for the 2014 Fifa cup */
        this.teamData = teamData;

        //Default values for the Table Headers
        this.tableHeaders = ["Delta Goals", "Result", "Wins", "Losses", "TotalGames"];

        /** To be used when sizing the svgs in the table cells.*/
        this.cell = {
            "width": 70,
            "height": 20,
            "buffer": 15
        };

        this.bar = {
            "height": 20
        };

        /** Set variables for commonly accessed data columns*/
        this.goalsMadeHeader = 'Goals Made';
        this.goalsConcededHeader = 'Goals Conceded';

        /** Setup the scales*/
        this.goalScale = null; 

        /** Used for games/wins/losses*/
        this.gameScale = null; 

        /**Color scales*/
        /**For aggregate columns  Use colors '#ece2f0', '#016450' for the range.*/
        this.aggregateColorScale = null; 

        /**For goal Column. Use colors '#cb181d', '#034e7b'  for the range.*/
        this.goalColorScale = null; 
    }


    /**
     * Creates a table skeleton including headers that when clicked allow you to sort the table by the chosen attribute.
     * Also calculates aggregate values of goals, wins, losses and total games as a function of country.
     *
     */
    createTable() {
        const MAX_GOALS = Math.max(...this.teamData.map(d => d.value['Goals Made']));
        const MAX_GAMES = Math.max(...this.teamData.map(d => d.value['Total Games']));
        
        this.goalScale = d3.scaleLinear()
            .domain([0, MAX_GOALS])
            .range([0, this.cell["width"] * 2])
            .nice();
        
        this.gameScale = d3.scaleLinear()
            .domain([0, MAX_GAMES])
            .range([0, this.cell["width"]])
            .nice();
        
        this.aggregateColorScale = d3.scaleLinear()
            .domain([0, MAX_GAMES])
            .range(["#ece2f0", "#016450"]);
        
        this.goalColorScale = d3.scaleLinear()
            .domain([0, 1])
            .range(["#034e7b", "#cb181d"]);

        // create the x axes for the goalScale.
        let goalAxis = d3.axisTop(this.goalScale);

        // add GoalAxis to header of col 1.
        d3.select("#goalHeader")
            .append("svg")
            .attr("height", this.cell["height"] * 1.1)
            .attr("width", this.cell["width"] * 2.4)
            .append("g")
            .attr("transform", "translate(17.5,20)")
            .call(goalAxis);

        // add sorting when column labels are clicked
        d3.select("#matchTable")
            .select("thead")
            .select("tr")
            .selectAll("td")
            .classed("unsorted", true)
            .on("click", function() {
                this.tableElements = this.tableElements.filter(d => d.value.type == "aggregate");
                this.sortByColumn(d3.event.target);
                this.updateTable();
            }.bind(this));
        d3.select("#matchTable")
            .select("thead")
            .select("tr")
            .selectAll("th")
            .classed("unsorted", true)
            .on("click", function() {
                this.tableElements = this.tableElements.filter(d => d.value.type == "aggregate");
                this.sortByColumn(d3.event.target);
                this.updateTable();
            }.bind(this));
    }

    sortByColumn(selectedColumn) {
        let sortAscending = Boolean(selectedColumn.className == "unsorted" || selectedColumn.className == "descending");
        switch (selectedColumn.id) {
            case "team":
                sortAscending ? this.tableElements.sort((a, b) => a.key.localeCompare(b.key)) 
                    : this.tableElements.sort((a, b) => b.key.localeCompare(a.key));
                break;
            case "goals":
                sortAscending ? this.tableElements.sort((a, b) => b.value['Goals Made'] - a.value['Goals Made']) 
                    : this.tableElements.sort((a, b) => a.value['Goals Made'] - b.value['Goals Made']);
                break;
            case "results":
                sortAscending ? this.tableElements.sort((a, b) => b.value['Result']['ranking'] - a.value['Result']['ranking']) 
                    : this.tableElements.sort((a, b) => a.value['Result']['ranking'] - b.value['Result']['ranking']);
                break;
            case "wins":
                sortAscending ? this.tableElements.sort((a, b) => b.value['Wins'] - a.value['Wins']) 
                    : this.tableElements.sort((a, b) => a.value['Wins'] - b.value['Wins']);
                break;
            case "losses":
                sortAscending ? this.tableElements.sort((a, b) => b.value['Losses'] - a.value['Losses']) 
                    : this.tableElements.sort((a, b) => a.value['Losses'] - b.value['Losses']);
                break;
            case "total":
                sortAscending ? this.tableElements.sort((a, b) => b.value['Total Games'] - a.value['Total Games']) 
                    : this.tableElements.sort((a, b) => a.value['Total Games'] - b.value['Total Games']);
                break;
        }
        selectedColumn.className = sortAscending ? "ascending" : "descending";
    }


    /**
     * Updates the table contents with a row for each element in the global variable tableElements.
     */
    updateTable() {
        // clear previous rows
        d3.select("#matchTable").select("tbody").selectAll("tr").remove();

        // create table rows
        let rows = d3.select("#matchTable").select("tbody")
            .selectAll("tr")
            .data(this.tableElements)
            .enter()
            .append("tr");
        
        rows.on("mouseenter", function(d) {
            if (d.value.type == "game") {
                this.tree.updateTree(d.value['Opponent'] + d.key);
            } else {
                this.tree.updateTree(d.key);
            }
        }.bind(this));

        rows.on("mouseleave", function(d) {
            this.tree.clearTree();
        }.bind(this));
        
        // append th elements for the Team Names
        let ths = rows.selectAll("th")
            .data(d => [{ "name" : d.key, "type" : d.value['type']}])
            .enter()
            .append("th")
            .attr("class", d => d.type)
            .html(function(d) {
                return d.type == "game" ? "x" + d.name : d.name;
            });
        
        // add style for team names for game rows
        ths.filter(d => d.type == "game").classed("game", true);
        
        // click event to expand/collapse game information
        ths.on("click", function(d) {
            for (let i = 0; i < this.tableElements.length; i++) {
                if (d.name == this.tableElements[i].key) {
                    this.updateList(i);
                    return;
                }
            }
        }.bind(this));

        // create each column and pass down the data
        let tds = rows.selectAll("td")
            .data(d => [{ "type" : d.value['type'], "vis" : "goals", 
                            "value" : [d.value['Goals Made'], d.value['Goals Conceded']] }, // goals
                        { "type" : d.value['type'], "vis" : "text", "value" : d.value['Result'] }, // results
                        { "type" : d.value['type'], "vis" : "bar", "value" : d.value['Wins'] }, // wins
                        { "type" : d.value['type'], "vis" : "bar", "value" : d.value['Losses'] }, // losses
                        { "type" : d.value['type'], "vis" : "bar", "value" : d.value['Total Games'] }]) // total games
            .enter()
            .append("td");
        
        // create results column
        let resultsColumns = tds.filter(d => d.vis == "text");
        resultsColumns.append("svg")
            .attr("width", this.cell['width'] * 2)
            .attr("height", this.cell['height'])
            .append("text")
            .attr("y", this.cell['height'] * 0.75)
            .text(d => d.value['label']);

        // create bars for the "wins", "losses", and "total games" columns
        let barColumns = tds.filter(d => d.vis == "bar" && d.type == "aggregate");
        barColumns.append("svg")
            .attr("width", this.cell['width'])
            .attr("height", this.cell['height'])
            .append("rect")
            .attr("width", d => this.gameScale(d.value))
            .attr("height", this.bar['height'])
            .attr("fill", d => this.aggregateColorScale(d.value));
        barColumns.select("svg")
            .append("text")
            .classed("label", true)
            .attr("x", d => this.gameScale(d.value) - 10)
            .attr("y", this.cell['height'] * 0.75)
            .text(d => d.value);
        
        // create bar charts for the "goals" column
        let goalColumns = tds.filter(d => d.vis == "goals");
        goalColumns.append("svg")
            .attr("width", this.cell['width'] * 2 + 35)
            .attr("height", this.cell['height'])
            .attr("transform", "translate(0,0)")
            .append("rect")
            .classed("goalBar", true)
            .attr("width", d => this.goalScale(Math.abs(d.value[0] - d.value[1])))
            .attr("height", function(d) {
                return d.type == "aggregate" ? this.bar['height'] / 2 : this.bar['height'] / 4;
            }.bind(this))
            .attr("x", d => this.goalScale(Math.min(d.value[0], d.value[1])) + 17.5)
            .attr("y", function(d) {
                return d.type == "aggregate" ? 5 : 7.5;
            })
            .attr("fill", function(d) {
                // blue bar for a positive goal difference - red bar for a negative one
                if (d.value[0] > d.value[1]) {
                    return this.goalColorScale(0);
                }
                return this.goalColorScale(1);
            }.bind(this));

        // draw blue marks for made goals
        goalColumns.select("svg")
            .append("circle")
            .classed("goalCircle", true)
            .attr("cx", d => this.goalScale(d.value[0]) + 17.5)
            .attr("cy", this.cell['height'] * 0.5)
            .attr("stroke-width", 1)
            .attr("fill", function(d) {
                if (d.type == "game") {
                    return "white";
                } else if (d.value[0] == d.value[1]) {
                    return "grey";
                }
                return this.goalColorScale(0);
            }.bind(this))
            .attr("stroke", function(d) {
                return d.value[0] == d.value[1] ? "grey" : this.goalColorScale(0);
            }.bind(this));

        // draw red marks for conceded goals
        goalColumns.select("svg")
            .append("circle")
            .classed("goalCircle", true)
            .attr("cx", d => this.goalScale(d.value[1]) + 17.5)
            .attr("cy", this.cell['height'] * 0.5)
            .attr("fill", function(d) {
                if (d.type == "game") {
                    return "white";
                } else if (d.value[0] == d.value[1]) {
                    return "grey";
                }
                return this.goalColorScale(1);
            }.bind(this))
            .attr("stroke", function(d) {
                return d.value[0] == d.value[1] ? "grey" : this.goalColorScale(1);
            }.bind(this));

        //Add scores as title property to appear on hover

        //Populate cells (do one type of cell at a time )

        //Create diagrams in the goals column

        //Set the color of all games that tied to light gray

    };

    /**
     * Updates the global tableElements variable, with a row for each row to be rendered in the table.
     *
     */
    updateList(i) {
        let clickedElement = this.tableElements[i];
        // game clicked - do nothing
        if (clickedElement.value.type == "game") {
            return;
        } 
        // team clicked - display game information

        else if (this.elementIsAggregateEntry(i + 1)) {
            for (let j = 0; j < clickedElement.value.games.length; j++) {
                this.tableElements.splice((i + j + 1), 0, clickedElement.value.games[j]);
            }
            this.updateTable();
        } 
        // expanded team clicked - collpase game information
        else {
            this.collapseList();
        }
    }

    /**
     * Returns true if the element at the given index is an aggregate entry 
     * @param {Int} i  - index
     */
    elementIsAggregateEntry(i) {
        if (i == this.tableElements.length) {
            return this.tableElements[i - 1].value.type == "aggregate";
        }
        return this.tableElements[i].value.type == "aggregate";
    }

    /**
     * Collapses all expanded countries, leaving only rows for aggregate values per country.
     *
     */
    collapseList() {
        this.tableElements = this.tableElements.filter(d => d.value.type == "aggregate");
        this.updateTable();
    }


}
