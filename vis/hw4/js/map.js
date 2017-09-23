/** Class implementing the map view. */
class Map {
    /**
     * Creates a Map Object
     */
    constructor() {
        this.projection = d3.geoConicConformal().scale(150).translate([400, 350]);
        this.map = d3.select("#map");
    }

    /**
     * Function that clears the map
     */
    clearMap() {
        // Clear the styling for the hosting and participating teams
        this.map.selectAll("path")
            .classed("host", false)
            .classed("team", false)
        
        // Clear the gold and silver metal winner markers
        d3.select("#points").selectAll("circle").remove();
    }

    /**
     * Update Map with info for a specific FIFA World Cup
     * @param wordcupData the data for one specific world cup
     */
    updateMap(worldcupData) {

        // Clear any previous selections;
        this.clearMap();

        // Select the host country and change it's color accordingly.
        this.map.select("#" + worldcupData['host_country_code']).classed("host", true);

        // Iterate through all participating teams and change their color as well.
        let teamList = worldcupData['TEAM_LIST'].split(',');
        for (let i = 0; i < teamList.length; i++) {
            this.map.select("#" + teamList[i]).classed("team", true);
        }

        // Add gold metal winner marker
        d3.select("#points")
            .append("circle")
            .attr("cx", function() {
                let lon = worldcupData["WIN_LON"];
                let lat = worldcupData["WIN_LAT"];
                return this.projection([lon, lat])[0];
            }.bind(this))
            .attr("cy", function() {
                let lon = worldcupData["WIN_LON"];
                let lat = worldcupData["WIN_LAT"];
                return this.projection([lon, lat])[1];
            }.bind(this))
            .attr("r", 10)
            .classed("gold", true);

        // Add silver metal winner marker
        d3.select("#points")
            .append("circle")
            .attr("cx", function() {
                let lon = worldcupData["RUP_LON"];
                let lat = worldcupData["RUP_LAT"];
                return this.projection([lon, lat])[0];
            }.bind(this))
            .attr("cy", function() {
                let lon = worldcupData["RUP_LON"];
                let lat = worldcupData["RUP_LAT"];
                return this.projection([lon, lat])[1];
            }.bind(this))
            .attr("r", 7)
            .classed("silver", true);
    }

    /**
     * Renders the actual map
     * @param the json data with the shape of all countries
     */
    drawMap(world) {
        let data = topojson.feature(world, world.objects.countries);
        let path = d3.geoPath().projection(this.projection);

        // Draw countries
        this.map.selectAll("path")
            .data(data.features)
            .enter()
            .append("path")
            .attr("d", path)
            .attr("id", function(d) {
                return d.id;
            })
            .classed("countries", true);
        
        // Draw gradicule
        let graticule = d3.geoGraticule();
        this.map.append("path")
            .datum(graticule)
            .attr("class", "grat")
            .attr("d", path)
            .attr("fill", "none");

    }


}
