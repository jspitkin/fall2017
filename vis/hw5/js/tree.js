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

        // ******* TODO: PART VI *******
        console.log(treeData);
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

        // tree generation based off example from lecture notes (http://dataviscourse.net/tutorials/lectures/lecture-d3-layouts/)
        let treeGraphic = d3.select("#tree");
        let treeInfo = tree(root);
        let nodes = treeInfo.descendants();
        let links = treeInfo.descendants().slice(1);

        nodes.forEach(function(d) {
            let g = treeGraphic.append("g");
            g.classed("node", true);
            if (d.data['Wins'] == "1") {
                g.classed("winner", true);
            }
            // draw labels - leaf nodes on the right and the rest of on the left of the node
            if (d.children) {
                g.append("text")
                    .attr("x", d.y + PADDING_LEFT - 10)
                    .attr("y", d.x + 5)
                    .attr("text-anchor", "end")
                    .text(d.data['Team']);
            } else {
                g.append("text")
                    .attr("x", d.y + PADDING_LEFT + 10)
                    .attr("y", d.x + 5)
                    .attr("text-anchor", "start")
                    .text(d.data['Team']);
            }
            // draw edge
            if (d.parent != null) {
                let child = { "x" : d.x, "y" : d.y  + PADDING_LEFT};
                let parent = { "x" : d.parent.x, "y" : d.parent.y + PADDING_LEFT};
                g.append("path")
                    .classed("link", true)
                    .attr("d", this.diagonal(child, parent));
            }
            // draw node
            g.append("circle")
                .attr("cx", d.y + PADDING_LEFT)
                .attr("cy", d.x)
                .attr("r", 7);
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
    
    }

    /**
     * Removes all highlighting from the tree.
     */
    clearTree() {
        // ******* TODO: PART VII *******

        // You only need two lines of code for this! No loops! 
    }
}
