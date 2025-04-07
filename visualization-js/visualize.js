
let logger = {
    step: 0,
    numFoodEaten: 0,

    // next two values are placeholders, values are set in setup() function
    stepsTotal: 1000, // save steps num to be able to freeze the last step
    currentFrameRate: 30,
}
let frameRateButton1, frameRateButton2;
let initFrameRate = 30;
let output;
let stepCounter;

fetch('../output.json')
    .then(response => response.json())
    .then(data => {
        output = data
    })
    .catch(error => console.error(error));

function setup() {
    fetch('../output.json')
        .then(response => response.json())
        .then(output => {
            createCanvas(output.scene.width, output.scene.height);
            console.log(output);

            // create new HTML paragraph element to display step counter
            stepCounter = createP("Step: " + logger.step);

            // create new HTML paragraph element to display dead fish counter
            deadFishCounter = createP("Dead Fish: " + 0);

            // create new HTML paragraph element to display dead fish counter
            eatenFoodCounter = createP("Eaten food pieces: " + 0);

            // save max num of steps
            logger.stepsTotal = output.stepsTotal;

            // save frame rate
            logger.frameRate = initFrameRate
            frameRate(logger.frameRate);
            
            // Create the "Increase Frame Rate" button
            frameRateButton1 = createButton("Increase Frame Rate");
            // frameRateButton1.position(10, 10);
            frameRateButton1.mouseClicked(increaseFrameRate);
            
            // Create the "Decrease Frame Rate" button
            frameRateButton2 = createButton("Decrease Frame Rate");
            // frameRateButton2.position(10, 40);
            frameRateButton2.mouseClicked(decreaseFrameRate);

            // create new HTML paragraph element to display dead fish counter
            frameRateButton = createP("Frame Rate: " + logger.frameRate);

        })
        .catch(error => console.error(error));
}

function increaseFrameRate() {
    logger.frameRate += 5;
    frameRateButton.html("Frame Rate: " + logger.frameRate)
    frameRate(logger.frameRate); // Increase the frame rate by 5 frames per second
}

function decreaseFrameRate() {
    logger.frameRate -= 5;
    frameRateButton.html("Frame Rate: " + logger.frameRate)
    frameRate(logger.frameRate); // Decrease the frame rate by 5 frames per second
}

function render_step(output) {
    logger.step++
    let i = logger.step
    console.log(i)

    // do not log every step
    // if (i % 2 == 0) return

    clear();


    // render food
    output.steps[i].food.forEach(el => {
        push();
        fill('grey');
        stroke('grey');

        // draw the ellipse at the origin
        ellipse(el.x, el.y, 2, 2);

        pop();
    });


    // render fish
    output.steps[i].swarm.forEach(element => {
        // render alive fish
        if (element.alive == true) {
            // stroke(0);
            // fill(0);
            // ellipse(element.x, element.y, 10, 10);
            push();
            fill('black');

            // translate to where you want the center of the ellipse to be
            translate(element.x, element.y);

            // rotate using the frameCount (increases by one on each frame)
            rotate(-element.dir);

            // draw the ellipse at the origin
            ellipse(0, 0, output.fish_dim_x, output.fish_dim_y);
            pop();
        }
        // render dead fish
        else {
            let crossSize = 10; // set the size of the cross in pixels
            // stroke('red')
            push();
            stroke('red');
            line(element.x - crossSize / 2, element.y, element.x + crossSize / 2, element.y); // horizontal line
            line(element.x, element.y - crossSize / 2, element.x, element.y + crossSize / 2); // vertical line
            pop();
        }
    });


    // render sharks
    output.steps[i].sharks.forEach(el => {
        push();

        // translate to where you want the center of the ellipse to be
        translate(el.x, el.y);

        // rotate using the frameCount (increases by one on each frame)
        rotate(-el.dir);

        // draw the ellipse at the origin
        // fill('blue');
        noFill();
        stroke("blue")
        ellipse(0, 0, output.shark_dim_x, output.shark_dim_y);

        // // draw a "mouth" of the shark
        // fill('#d42a1e');
        // arc(0, 0, 30, 50, HALF_PI - QUARTER_PI / 2, HALF_PI + QUARTER_PI / 2, PIE);
        noFill();
        stroke('red')
        ellipse(0, output.shark_dim_y/2, output.shark_kill_radius * 2, output.shark_kill_radius * 2)

        // draw a SHARK_SENSE_DIST without their blind spot
        noFill();
        stroke("green")
        let rad = radians(output.shark_blind_angle_back);
        arc(0, 0, output.shark_sense_dist, output.shark_sense_dist, -HALF_PI + rad/2, HALF_PI + PI - rad/2, PIE);

        pop();
    });

    stepCounter.html("Step: " + i);
    deadFishCounter.html("Dead Fish: " + output.steps[i].deadFish)
    logger.numFoodEaten += output.steps[i].eatenFood;
    eatenFoodCounter.html("Eaten food pieces: " + logger.numFoodEaten)
}

function draw() {
    if (logger.step == 0) {
        fetch('../output.json')
            .then(response => response.json())
            .then(output => {
                render_step(output);
            })
            .catch(error => console.error(error));
    }
    else if (logger.step < logger.stepsTotal - 1) {
        render_step(output);
    }
}
