
let logger = {
    step: 0,
    stepsTotal: 2000 // save steps num to be able to freeze the last step
}

let output;
let stepCounter;
fetch('output.json')
    .then(response => response.json())
    .then(data => {
        output = data
    })
    .catch(error => console.error(error));

function setup() {
    fetch('output.json')
        .then(response => response.json())
        .then(output => {
            createCanvas(output.scene.width, output.scene.height);
            console.log(output);
                
            // create new HTML paragraph element to display step counter
            stepCounter = createP("Step: " + logger.step);

            // save max num of steps
            logger.stepsTotal = output.stepsTotal;
        })
        .catch(error => console.error(error));
}

function draw() {
    if (logger.step == 0) {
        fetch('output.json')
            .then(response => response.json())
            .then(output => {
                logger.step++;
                let i = logger.step;
                console.log(i);

                clear();

                // render fish
                output.steps[i].swarm.forEach(element => {
                    fill(0);
                    ellipse(element.x, element.y, 10, 10);
                });

                // render sharks
                output.steps[i].sharks.forEach(el => {
                    fill(0);
                    ellipse(el.x, el.y, 20, 30, Math.PI / 4, 0, 2 * Math.PI);
                });
                // fill(0);
                // ellipse(output.steps[i].shark.x, output.steps[i].shark.y, 50, 80, Math.PI / 4, 0, 2 * Math.PI);
                
                stepCounter.html("Step: " + i);
        
            })
            .catch(error => console.error(error));
    }
    else if (logger.step < logger.stepsTotal) {
        logger.step++
        let i = logger.step
        console.log(i)

        // do not log every step
        if (i % 2 == 0) return

        clear();

        // render fish
        output.steps[i].swarm.forEach(element => {
            // render alive fish
            if (element.alive == true) {
                stroke(0);
                fill(0);
                ellipse(element.x, element.y, 10, 10);
            }
            // render dead fish
            else {
                let crossSize = 10; // set the size of the cross in pixels
                stroke('red')
                line(element.x - crossSize / 2, element.y, element.x + crossSize / 2, element.y); // horizontal line
                line(element.x, element.y - crossSize / 2, element.x, element.y + crossSize / 2); // vertical line
            }
        });


        // render sharks
        // stroke(0);
        // fill('blue');
        // ellipse(output.steps[i].shark.x, output.steps[i].shark.y, 50, 80, Math.PI / 4, 0, 2 * Math.PI);
        output.steps[i].sharks.forEach(el => {
            stroke(0);
            fill('blue');
            ellipse(el.x, el.y, 50, 80, Math.PI / 4, 0, 2 * Math.PI);
        });
        

        stepCounter.html("Step: " + i);
    }
}
