/** Class implementing the infoPanel view. */
class InfoPanel {
    /**
     * Creates a infoPanel Object
     */
    constructor() {
    }

    /**
     * Update the info panel to show info about the currently selected world cup
     * @param oneWorldCup the currently selected world cup
     */
    updateInfo(oneWorldCup) {
        d3.select("#edition").html(oneWorldCup['EDITION']);
        d3.select("#host").html(oneWorldCup['host']);
        d3.select("#winner").html(oneWorldCup['winner']);
        d3.select("#silver").html(oneWorldCup['runner_up']);
        let teamsString = "<ul>";
        for (let i = 0; i < oneWorldCup['teams_names'].length; i++) {
            teamsString += "<li>" + oneWorldCup['teams_names'][i] + "</li>";
        }
        teamsString += "</ul>";
        d3.select("#teams").html(teamsString);
    }

}