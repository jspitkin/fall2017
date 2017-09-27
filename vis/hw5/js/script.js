/**
  * Loads in fifa-matches.csv file, aggregates the data into the correct format,
  * then calls the appropriate functions to create and populate the table.
  *
  */
d3.csv("data/fifa-matches.csv", function (error, matchesCSV) {

    let teamData = d3.nest()
        .key(d => d['Team'])
        .rollup(function(leaves) {
            let teamInfo = {
                'Goals Made' : d3.sum(leaves, d => d['Goals Made']),
                'Goals Conceded' : d3.sum(leaves, d => d['Goals Conceded']),
                'Delta Goals' : d3.sum(leaves, d => d['Delta Goals']),
                'Wins' : d3.sum(leaves, d => d['Wins']),
                'Losses' : d3.sum(leaves, d => d['Losses']),
                'Total Games' : leaves.length,
                'type' : "aggregate",
            };

            let games = d3.nest()
                .key(d => d['Opponent'])
                .rollup(function(game) {
                    let gameInfo = {
                        'Goals Made' : game[0]['Goals Made'],
                        'Goals Conceded' : game[0]['Goals Conceded'],
                        'Delta Goals' : game[0]['Delta Goals'],
                        'Wins' : game[0]['Wins'],
                        'Losses' : game[0]['Losses'],
                        'Opponent' : game[0]['Team'],
                        'Result' : { 'label' : game[0]['Result']},
                        'type' : 'game'
                    };
                    return gameInfo;
                })
                .entries(leaves);
            teamInfo["games"] = games;

            return teamInfo;
        })
        .entries(matchesCSV);
    
    console.log(teamData);

     /**
      * Loads in the tree information from fifa-tree.csv and calls createTree(csvData) to render the tree.
      *
      */
     d3.csv("data/fifa-tree.csv", function (error, treeCSV) {

        

     });

});
