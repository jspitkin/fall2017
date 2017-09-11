/**
 * Makes the first bar chart appear as a staircase.
 *
 * Note: use only the DOM API, not D3!
 */
function staircase() {
    let barChart = document.getElementById('a-bar');
    let bars = Array.from(barChart.children);
    let barHeights = bars.map(b => +b.getAttribute('height'));
    barHeights.sort((b1, b2) => b1 - b2);
    for (let i = 0; i < barHeights.length; i++) {
        barChart.children[i].setAttribute('height', barHeights[i]);
    }
}

/**
 * Render the visualizations
 * @param error
 * @param data
 */
function update(error, data) {
    if (error !== null) {
        alert('Could not load the dataset!');
    } else {
        // D3 loads all CSV data as strings;
        // while Javascript is pretty smart
        // about interpreting strings as
        // numbers when you do things like
        // multiplication, it will still
        // treat them as strings where it makes
        // sense (e.g. adding strings will
        // concatenate them, not add the values
        // together, or comparing strings
        // will do string comparison, not
        // numeric comparison).

        // We need to explicitly convert values
        // to numbers so that comparisons work
        // when we call d3.max()

        for (let d of data) {
            d.a = +d.a;
            d.b = +d.b;
        }
    }

    // Set up the scales
    let aScale = d3.scaleLinear()
        .domain([0, d3.max(data, d => d.a)])
        .range([0, 150]);
    let bScale = d3.scaleLinear()
        .domain([0, d3.max(data, d => d.b)])
        .range([0, 150]);
    let iScale = d3.scaleLinear()
        .domain([0, data.length])
        .range([0, 110]);

    // ****** PART III (you will also edit in PART V) ******

    // Select and update the 'a' bar chart bars
    let barChartA = d3.select('#a-bar');
    let barsA = barChartA.selectAll('rect').data(data);
    // Remove old bar elements 
    barsA.exit()
        .transition()
        .duration(1000)
        .attr('height', 0)
        .remove();
    // Add the 'enter' elements and merge 'update' elements
    barsA = barsA.enter().append('rect').merge(barsA);
    // Set attributes of new elements 
    barsA.transition()
        .duration(1000)
        .attr('height', function(d) {
            return aScale(d.a);
        });
    barsA.attr('x', function(d, i) {
            return (i + 1) * 10;
        })
        .attr('y', 0)
        .attr('width', 10);

    // Select and update the 'b' bar chart bars
    let barChartB = d3.select('#b-bar');
    let barsB = barChartB.selectAll('rect').data(data);
    // Remove old bar elements
    barsB.exit()
        .transition()
        .duration(1000)
        .attr('height', 0)
        .remove();
    // Add the 'enter' elements and merge 'update' elements
    barsB = barsB.enter().append('rect').merge(barsB);
    // Set attributes of new elements
    barsB.transition()
        .duration(1000)
        .attr('height', function(d) {
            return bScale(d.b);
        })
    barsB.attr('x', function(d, i) {
            return (i + 1) * 10;
        })
        .attr('y', 0)
        .attr('width', 10);

    // Select and update the 'a' line chart path using this line generator
    let aLineGenerator = d3.line()
        .x((d, i) => iScale(i))
        .y((d) => aScale(d.a));
    
    let lineChartA = d3.select('#a-line');
    lineChartA.select('path')
        .attr('d', aLineGenerator(data))

    // Select and update the 'b' line chart path (create your own generator)
    let bLineGenerator = d3.line()
        .x((d, i) => iScale(i))
        .y((d) => bScale(d.b));

    let lineChartB = d3.select('#b-line');
    lineChartB.select('path')
        .attr('d', bLineGenerator(data));

    // Select and update the 'a' area chart path
    let aAreaGenerator = d3.area()
        .x((d, i) => iScale(i))
        .y0(0)
        .y1(d => aScale(d.a));
    
    let areaChartA = d3.select('#a-area');
    areaChartA.select('path')
        .attr('d', aAreaGenerator(data));

    // Select and update the 'b' area chart path
    let bAreaGenerator = d3.area()
        .x((d, i) => iScale(i))
        .y0(0)
        .y1(d => bScale(d.b))
    
    let areaChartB = d3.select('#b-area');
    areaChartB.select('path')
        .attr('d', bAreaGenerator(data));

    // Select the scatterplot points
    let scatterplot = d3.select('#scatterplot');
    let points = scatterplot.selectAll('circle').data(data);
    // Remove old points
    points.exit().remove();
    // Add the 'enter' points and merge with 'update' points
    points = points.enter().append('circle').merge(points)
    // Set attributes of each point
    points.attr('r', 5)
        .attr('cx', function(d) {
            return aScale(d.a);
        })
        .attr('cy', function(d) {
            return bScale(d.b);
        })
        .append('svg:title')
        .text(function(d) {
            let x = parseFloat(d.a.toFixed(2));
            let y = parseFloat(d.b.toFixed(2));
            return '(' + x + ', ' + y + ')';
        });
   
    // ****** PART IV ******
    let barA = document.getElementById('a-bar');
    for (let bar of barA.children) {
        bar.addEventListener('mouseenter', function(event) {
           bar.style.fill = "lightsteelblue"; 
        });
        bar.addEventListener('mouseleave', function(event) {
            bar.style.fill = "steelblue";
        });
    }

    let barB = document.getElementById('b-bar');
    for (let bar of barB.children) {
        bar.addEventListener('mouseenter', function(event) {
            bar.style.fill = "lightsteelblue";
        });
        bar.addEventListener('mouseleave', function(event) {
            bar.style.fill = "steelblue";
        });
    }
}

/**
 * Load the file indicated by the select menu
 */
function changeData() {
    let dataFile = document.getElementById('dataset').value;
    if (document.getElementById('random').checked) {
        randomSubset();
    }
    else {
        d3.csv('data/' + dataFile + '.csv', update);
    }
}

/**
 *   Load the file indicated by the select menu, and then slice out a random chunk before passing the data to update()
 */
function randomSubset() {
    let dataFile = document.getElementById('dataset').value;
    if (document.getElementById('random').checked) {
        d3.csv('data/' + dataFile + '.csv', function (error, data) {
            let subset = [];
            for (let d of data) {
                if (Math.random() > 0.5) {
                    subset.push(d);
                }
            }
            update(error, subset);
        });
    }
    else {
        changeData();
    }
}