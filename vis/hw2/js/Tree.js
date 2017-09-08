/** Class representing a Tree. */
class Tree {
	/**
	 * Creates a Tree Object
	 * parentNode, children, parentName,level,position
	 * @param {json[]} json - array of json object with name and parent fields
	 */
	constructor(json) {
		// Model
		this.nodes = [];
		this.root = null;

		// View
		this.posScalingX = 210;
		this.posScalingY = 100;
		this.offsetX = 100;
		this.offsetY = 50;
		this.nodeRadius = 42;
		this.svgHeight = 1000;
		this.svgWidth = 1000;

		// Read in nodes from JSON file
		for (let entry of json) {
			let node = new Node(entry.name, entry.parent);
			this.nodes.push(node);	

			// Assign the root node of the tree
			if (node.parentName === "root") {
				this.root = node;
			}
		}

		// Populate parentNode field
		for (let node of this.nodes) {
			let parentNode = node;
			let childrenNodes = this.nodes.filter(n => n.parentName == parentNode.name);
			for (let childNode of childrenNodes) {
				childNode.parentNode = parentNode;
			}
		}

	}

	/**
	 * Function that builds a tree from a list of nodes with parent refs
	 */
	buildTree() {
		// Populate children field
		for (let node of this.nodes) {
			let parentNode = node;
			parentNode.children = this.nodes.filter(n => n.parentName == parentNode.name);
		}
		// Recursively assign each node's level
		this.assignLevel(this.root, 0);
		// Recursively assign each node's position
		this.assignPosition(this.root, 0);
	}

	/**
	 * Recursive function that assign positions to each node
	 */
	assignPosition(node, position) {
		node.position = position;
		for (let childNode of node.children) {
			let position = this.determinePosition(childNode);
			this.assignPosition(childNode, position);
		}
	}

	/**
	 * Determines the position for a given node
	 */
	determinePosition(node) {
		// If we'are at the root - return 0
		if (!node.parentNode) {
			return 0;
		}
		// Find the greatest - parent's pos or nodes level's max pos + 1
		let parentPos = node.parentNode.position;
		let levelNodes = this.nodes.filter(n => n.level == node.level);
		let levelMax = Math.max.apply(null, levelNodes.map(n => n.position));

		return Math.max(parentPos, levelMax + 1);
	}

	/**
	 * Recursive function that assign levels to each node
	 */
	assignLevel(node, level) {
		node.level = level;
		for (let childNode of node.children) {
			this.assignLevel(childNode, level + 1);
		}
	}

	/**
	 * Function that renders the tree
	 */
	renderTree() {
		let svg = d3.select("body")
					.append("svg")
					.attr("width", this.svgWidth)
					.attr("height", this.svgHeight);
		
		this.renderLines(svg);
		this.renderNodes(svg);
		this.renderLabels(svg);
	}

	/**
	 * Renders lines connecting each node in the tree
	 * @param {svg} svg - the containing svg element
	 */
	renderLines(svg) {
		for (let parentNode of this.nodes) {
			let childrenNodes = parentNode.children;
			for (let childNode of childrenNodes) {
				let line = svg.append("line");
				line.attr("x1", parentNode.level * this.posScalingX + this.offsetX)
					.attr("y1", parentNode.position * this.posScalingY + this.offsetY)
					.attr("x2", childNode.level * this.posScalingX + this.offsetX)
					.attr("y2", childNode.position * this.posScalingY + this.offsetY);
			}
		}
	}

	/**
	 * Renders each node based on their position and level 
	 * @param {svg} svg - the containing svg element 
	 */
	renderNodes(svg) {
		let nodes = svg.selectAll("circle")
					   .data(this.nodes)
					   .enter()
					   .append("circle");

		nodes.attr("cx", function(d) {
				return (d.level * this.posScalingX) + this.offsetX;
			}.bind(this))
			.attr("cy", function(d) {
				return (d.position * this.posScalingY) + this.offsetY;
			}.bind(this))
			.attr("r", function(d) {
				return this.nodeRadius;
			}.bind(this));
	}

	/**
	 * Renders labels on each node in the tree 
	 * @param {svg} svg - the containing svg element
	 */
	renderLabels(svg) {
		let nodeTexts = svg.selectAll("text")
						   .data(this.nodes)
						   .enter()
						   .append("text");
		
		nodeTexts.attr("x", function(d) {
			return (d.level * this.posScalingX) + this.offsetX;
		}.bind(this))
		.attr("y", function(d) {
			return (d.position * this.posScalingY) + this.offsetY;
		}.bind(this))
		.text(function(d) {
			return d.name;
		})
		.attr("class", "label");
	}
		
}