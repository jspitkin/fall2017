/** Class implementing the tree view. */
class Tree {
    /**
     * Creates a Tree Object
     */
    constructor() {
        
    }

    /**
     * Creates a node/edge structure and renders a tree layout based on the input data
     *
     * @param treeData an array of objects that contain parent/child information.
     */
    createTree(treeData) {
        const WIDTH = 800;
        const HEIGHT = 300;
        const PADDING_LEFT = 90;

        //Create a tree and give it a size() of 800 by 300. 
        let tree = d3.tree();
        tree.size([WIDTH, HEIGHT]);

        //Create a root for the tree using d3.stratify(); 
        let root = d3.stratify()
            .id(d => d.id)
            .parentId(function(d) {
                return d.ParentGame == "" ? null : treeData[d.ParentGame].id;
            })
            (treeData);

        let treeGraphic = d3.select("#tree");
        let nodes = tree(root).descendants();

        // render edges
        nodes.forEach(function(d) {
            let g = treeGraphic.append("g");
            if (d.children) {
                let childOne = { "x" : d.children[0].x,
                                 "y" : d.children[0].y  + PADDING_LEFT};
                let childTwo = { "x" : d.children[1].x,
                                 "y" : d.children[1].y + PADDING_LEFT };
                let parent = { "x" : d.x, 
                               "y" : d.y + PADDING_LEFT};
                let childOneTeam = d.children[0].data['Team'];
                let childTwoTeam = d.children[1].data['Team'];
                g.append("path")
                    .classed("link", true)
                    .classed(childOneTeam + childTwoTeam, true)
                    .attr("d", this.diagonal(childOne, parent));
                g.append("path")
                    .classed("link", true)
                    .classed(childOneTeam + childTwoTeam, true)
                    .attr("d", this.diagonal(childTwo, parent));
                // add class for links with matching team nodes
                if (d.data['Team'] == d.children[0].data['Team']) {
                    g.select("path").classed(d.data['Team'], true);
                } else if (d.data['Team'] == d.children[1].data['Team']) {
                    g.select("path").classed(d.data['Team'], true);
                }
            }
        }.bind(this));

        // render nodes
        nodes.forEach(function(d) {
            let g = treeGraphic.append("g")
                .classed("node", true);
            if (d.data['Wins'] == "1") {
                g.classed("winner", true);
            }
            g.append("circle")
                .attr("cx", d.y + PADDING_LEFT)
                .attr("cy", d.x)
                .attr("r", 7);
        }.bind(this));

        // render labels
        nodes.forEach(function(d) {
            // leaf nodes on the right and the rest of on the left of the node
            let g = treeGraphic.append("g");
            if (d.children) {
                g.append("text")
                    .attr("x", d.y + PADDING_LEFT - 10)
                    .attr("y", d.x + 5)
                    .attr("text-anchor", "end")
                    .attr("id", d.id)
                    .classed(d.data['Team'], true)
                    .text(d.data['Team']);
            // set class to highlight label for a specific game
            } else {
                g.append("text")
                    .attr("x", d.y + PADDING_LEFT + 10)
                    .attr("y", d.x + 5)
                    .attr("text-anchor", "start")
                    .attr("id", d.id)
                    .classed(d.data['Team'], true)
                    .text(d.data['Team']);
            }
        }.bind(this));

        // add classes to labels for single game highlighting
        nodes.forEach(function(d) {
            if (d.children) {
                let childOneTeam = d.children[0].data['Team'];
                let childTwoTeam = d.children[1].data['Team'];
                let childOneLabel = d3.select("text#" + d.children[0].id);
                let childTwoLabel = d3.select("text#" + d.children[1].id);
                childOneLabel.classed(childOneTeam + childTwoTeam, true);
                childTwoLabel.classed(childOneTeam + childTwoTeam, true);
            }
        }.bind(this));
    }

    // taken from the class lecture notes (http://dataviscourse.net/tutorials/lectures/lecture-d3-layouts/)
    diagonal(s, d) {
        let path = `M ${s.y} ${s.x}
                C ${(s.y + d.y) / 2} ${s.x},
                    ${(s.y + d.y) / 2} ${d.x},
                    ${d.y} ${d.x}`;
        return path;
    }

    /**
     * Updates the highlighting in the tree based on the selected team.
     * Highlights the appropriate team nodes and labels.
     *
     * @param row a string specifying which team was selected in the table.
     */
    updateTree(row) {
        // ******* TODO: PART VII *******
        d3.selectAll("path." + row).classed("selected", true);
        d3.selectAll("text." + row).classed("selectedLabel", true);
    }

    /**
     * Removes all highlighting from the tree.
     */
    clearTree() {
        d3.selectAll(".selected").classed("selected", false);
        d3.selectAll(".selectedLabel").classed("selectedLabel", false);
    }
}
