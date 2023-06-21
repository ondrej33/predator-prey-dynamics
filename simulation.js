let Scene = {
  w : 800, 
  h : 600, 
  swarm : new Set(), 
  num_fish : 200,
  shark: null,

  // TODO: change this based on actual fish and shark behaviour
  fish_sense_dist : 30, // distance for fish senses
  shark_sense_dist: 50, // distance for shark senses

  // get neighbors for prey fish up to certain distance
  fish_neighbours : function(x) {
    let r = [];
    for (let p of this.swarm) {
      if (dist(p.pos.x, p.pos.y, x.x, x.y) <= this.fish_sense_dist) {
        r.push(p);
      }
    }
    return r;
  },

  // get neighbors for predator shark up to certain distance
  shark_neighbours : function(x) {
    let r = [];
    for (let p of this.swarm) {
      if (dist(p.pos.x, p.pos.y, x.x, x.y) <= this.shark_sense_dist) {
        r.push(p);
      }
    }
    return r;
  },

  // general function to get neighbours up to certain distance
  eaten_neighbours : function(x) {
    let r = [];
    for (let p of this.swarm) {
      if (dist(p.pos.x, p.pos.y, x.x, x.y) <= this.shark.kill_radius) {
        r.push(p);
      }
    }
    return r;
  },

  // Add outer boundaries of the canvas 
  // we use "cyclic" boundaries for now
  wrap : function(x) {
    if (x.x < 0) x.x += this.w;
    if (x.y < 0) x.y += this.h;
    if (x.x >= this.w) x.x -= this.w;
    if (x.y >= this.h) x.y -= this.h;
  }

}

// Object for logging information, may still be useful for something
let logger = {
  // step of the simulation
  step: 0,
}

class Fish {
  constructor(id) {
    this.pos = createVector(random(0, Scene.w), random(0, Scene.h));
    this.dir = p5.Vector.random2D();
    this.id = id;
  }

  // TODO: re-implement the forces based on actual Fish behaviour
  step() {
    let N=0;
    let avg_sin = 0, avg_cos = 0;
    let avg_p = createVector(0, 0);
    let avg_d = createVector(0, 0);

    // compute average angle and average position
    // avg angle for allignment, avg pos for cohesion
    for (let n of Scene.fish_neighbours(this.pos)) {
      avg_p.add(n.pos);

      // separation
      if (n != this) {  
        let away = p5.Vector.sub(this.pos, n.pos);
        away.div(away.magSq());
        avg_d.add(away);
      }

      avg_sin += Math.sin(n.dir.heading());
      avg_cos += Math.cos(n.dir.heading());
      N++;
    }
    // divide everything by N (we want average values)
    avg_sin /= N, avg_cos /= N, avg_p.div(N), avg_d.div(N);

    let avg_angle = Math.atan2(avg_sin, avg_cos);

    // add some random noise to the angle    
    avg_angle += random(-0.25, 0.25);
    
    this.dir = p5.Vector.fromAngle(avg_angle);

    // implement the cohesion
    let cohesion = p5.Vector.sub(avg_p, this.pos);
    cohesion.div(20);
    this.dir.add(cohesion);

    // add separation
    avg_d.mult(20);
    this.dir.add(avg_d);

    // add repulsive force from shark if it is near the fish
    let shark_pos = Scene.shark.pos;
    if (dist(shark_pos.x, shark_pos.y, this.pos.x, this.pos.y) <= Scene.fish_sense_dist) {
      let shark_repulsion_vec = p5.Vector.sub(this.pos, shark_pos);
      shark_repulsion_vec.div(shark_repulsion_vec.mag()); // normalize
      this.dir.add(shark_repulsion_vec);
    }
    this.pos.add(this.dir);
    Scene.wrap(this.pos);
  }

  draw() {
    fill(0);
    ellipse(this.pos.x, this.pos.y, 10, 10);
  }
}

class Shark {
  constructor(id) {
    this.pos = createVector(random(0, Scene.w), random(0, Scene.h));
    this.dir = p5.Vector.random2D();
    this.id = id;
    this.kill_radius = 20;
  }

  // TODO: re-implement the forces based on actual Shark behaviour
  step() {
    let N=0;
    let avg_p = createVector(0, 0);

    // compute the average position of neighbouring fish
    for (let n of Scene.shark_neighbours(this.pos)) {
      avg_p.add(n.pos);
      N++;
    }

    if (N == 0) {
      // if no neighbours, shift randomly for a bit
      let avg_angle = random(-0.5, 0.5);
      this.dir = p5.Vector.fromAngle(avg_angle);
    } else {
      // otherwise go for the average position of neighbouring fish
      avg_p.div(N);
      let hunt_vector = p5.Vector.sub(avg_p, this.pos);
      hunt_vector.div(hunt_vector.magSq()); // normalize by its magnitude
      this.dir.add(hunt_vector);
    }

    this.pos.add(this.dir);
    Scene.wrap(this.pos);
  }

  draw() {
    fill(0);
    ellipse(this.pos.x, this.pos.y, 50, 80, Math.PI / 4, 0, 2 * Math.PI);
  }
}

function setup() {
  createCanvas(Scene.w, Scene.h);

  // generate fish
  for (let i = 0; i < Scene.num_fish; i++) {
    Scene.swarm.add(new Fish(i));
  }

  // generate shark
  Scene.shark = new Shark(0);
}

// draw and update logger
function draw() {
  clear();

  // new step
  logger.step++;
  
  // move fish
  for (let p of Scene.swarm) {
    p.step();
    p.draw();
  }

  // move shark
  Scene.shark.step();
  Scene.shark.draw();

  // remove fish that were eaten in this step
  let eaten_fish = Scene.eaten_neighbours(Scene.shark.pos);
  let counter_eaten = 0;
  for (let p of eaten_fish) {
    Scene.swarm.delete(p);
    counter_eaten++;
  }
  if (counter_eaten > 0) {
    console.log("Step "+logger.step+": eaten "+counter_eaten+" fish");
  }
}
