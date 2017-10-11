/**
  * Loads in fifa-matches.csv file, aggregates the data into the correct format,
  * then calls the appropriate functions to create and populate the table.
  *
  */
d3.csv("data/fifa-matches.csv", function (error, matchesCSV) {

    let rankingDict = { 'Group' : 0,
                        'Round of Sixteen' : 1,
                        'Quarter Finals' : 2, 
                        'Semi Finals' : 3,
                        'Fourth Place' : 4,
                        'Third Place' : 5,
                        'Runner-Up' : 6,
                        'Winner' : 7 };

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

            let label = "Group";
            let ranking = 0;
            for (let leaf of leaves) {
                if (rankingDict[leaf['Result']] > ranking) {
                    label = leaf['Result'];
                    ranking = rankingDict[leaf['Result']];
                }
            }
            let result = { 'label' : label, 'ranking' : ranking};
            teamInfo['Result'] = result;

            let games = d3.nest()
                .key(d => d['Opponent'])
                .rollup(function(games) {
                    let gameInfo = {
                        'Goals Made' : games[0]['Goals Made'],
                        'Goals Conceded' : games[0]['Goals Conceded'],
                        'Delta Goals' : games[0]['Delta Goals'],
                        'Wins' : games[0]['Wins'],
                        'Losses' : games[0]['Losses'],
                        'Opponent' : games[0]['Team'],
                        'Result' : games[0]['Result'],
                        'type' : 'game'
                    };

                    let label = "Group";
                    let ranking = 0;
                    for (let game of games) {
                        if (rankingDict[game['Result']] > ranking) {
                            label = game['Result'];
                            ranking = rankingDict[game['Result']];
                        }
                    }
                    let result = { 'label' : label, 'ranking' : ranking};
                    gameInfo['Result'] = result;

                    return gameInfo;
                })
                .entries(leaves);
            teamInfo["games"] = games;

            return teamInfo;
        })
        .entries(matchesCSV);
    

    /**
     * Loads in the tree information from fifa-tree.csv and calls createTree(csvData) to render the tree.
     *
     */
    d3.csv("data/fifa-tree.csv", function (error, csvData) {
        
                //Create a unique "id" field for each game
                csvData.forEach(function (d, i) {
                    d.id = d.Team + d.Opponent + i;
                });
        
                //Create Tree Object
                let tree = new Tree();
                tree.createTree(csvData);
        
                //Create Table Object and pass in reference to tree object (for hover linking)
                let table = new Table(teamData,tree);
        
                table.createTable();
                table.updateTable();
            });

});
