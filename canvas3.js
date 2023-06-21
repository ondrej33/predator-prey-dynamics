let Scene = {
    w : 1000, h : 800, swarm : [],
  
    // get neighbors up to certain distance
    neighbours : function(x) {
      let r = []
      for (let p of this.swarm) {
        if (dist(p.pos.x, p.pos.y, x.x, x.y) <= 25) {
          r.push(p)
        }
      }
      return r
    },
  
    // Add outer boundaries of the canvas - we use "cyclic" boundaries
    wrap : function(x) {
      if (x.x < 0) x.x += this.w
      if (x.y < 0) x.y += this.h
      if (x.x >= this.w) x.x -= this.w
      if (x.y >= this.h) x.y -= this.h
    }
  }
  
  let px_offset = 200
  let m_to_px = 100
  
  // Object of the racetrack, holds points of the inner + outer edge, and mid point
  let racetrack = {
    outer: [[px_offset, px_offset],
            [px_offset + 6.4*m_to_px, px_offset],
            
            [px_offset + 6.4*m_to_px + 0.3*m_to_px, px_offset + 0.1*m_to_px],
            [px_offset + 6.4*m_to_px + 0.5*m_to_px, px_offset + 0.25*m_to_px],
            [px_offset + 6.4*m_to_px + 0.8*m_to_px, px_offset + 0.5*m_to_px],
            [px_offset + 6.4*m_to_px + 0.9*m_to_px, px_offset + 0.7*m_to_px],
            [px_offset + 6.4*m_to_px + 1*m_to_px, px_offset + 0.9*m_to_px],
            [px_offset + 6.4*m_to_px + 1.1*m_to_px, px_offset + 1.3*m_to_px],
            [px_offset + 6.4*m_to_px + 1.2*m_to_px, px_offset + 1.9*m_to_px],
            [px_offset + 6.4*m_to_px + 1.2*m_to_px, px_offset + 2.5*m_to_px],
            [px_offset + 6.4*m_to_px + 1.2*m_to_px, px_offset + 2.8*m_to_px],
            [px_offset + 6.4*m_to_px + 1.1*m_to_px, px_offset + 3.4*m_to_px],
            [px_offset + 6.4*m_to_px + 1*m_to_px, px_offset + 3.8*m_to_px],
            [px_offset + 6.4*m_to_px + 0.9*m_to_px, px_offset + 4*m_to_px],
            [px_offset + 6.4*m_to_px + 0.8*m_to_px, px_offset + 4.2*m_to_px],
            [px_offset + 6.4*m_to_px + 0.5*m_to_px, px_offset + 4.4*m_to_px],
            [px_offset + 6.4*m_to_px + 0.3*m_to_px, px_offset + 4.5*m_to_px],
            
            [px_offset + 6.4*m_to_px, px_offset + 4.5*m_to_px],
            [px_offset, px_offset + 4.5*m_to_px],
           
           [px_offset - 0.3*m_to_px, px_offset + 4.5*m_to_px],
            [px_offset - 0.5*m_to_px, px_offset + 4.4*m_to_px],
            [px_offset - 0.8*m_to_px, px_offset + 4.2*m_to_px],
            [px_offset - 0.9*m_to_px, px_offset + 4*m_to_px],
            [px_offset - 1*m_to_px, px_offset + 3.8*m_to_px],
            [px_offset - 1.1*m_to_px, px_offset + 3.4*m_to_px],
            [px_offset - 1.2*m_to_px, px_offset + 2.8*m_to_px],
            [px_offset - 1.2*m_to_px, px_offset + 2.5*m_to_px],
            [px_offset - 1.2*m_to_px, px_offset + 1.9*m_to_px],
            [px_offset - 1.1*m_to_px, px_offset + 1.3*m_to_px],
            [px_offset - 1*m_to_px, px_offset + 0.9*m_to_px],
            [px_offset - 0.9*m_to_px, px_offset + 0.7*m_to_px],
            [px_offset - 0.8*m_to_px, px_offset + 0.5*m_to_px],
            [px_offset - 0.5*m_to_px, px_offset + 0.25*m_to_px],
            [px_offset - 0.3*m_to_px, px_offset + 0.1*m_to_px],
            
           ],
    inner: [[px_offset +1.2*m_to_px, px_offset + 0.8*m_to_px],
            [px_offset +5.2*m_to_px, px_offset + 0.8*m_to_px],
            
            [px_offset +5.2*m_to_px + 0.3*m_to_px, px_offset +0.8*m_to_px + 0.64* 0.1*m_to_px],
            [px_offset +5.2*m_to_px + 0.5*m_to_px, px_offset +0.8*m_to_px + 0.64* 0.25*m_to_px],
            [px_offset +5.2*m_to_px + 0.8*m_to_px, px_offset +0.8*m_to_px + 0.64* 0.5*m_to_px],
            [px_offset +5.2*m_to_px + 0.9*m_to_px, px_offset +0.8*m_to_px + 0.64* 0.7*m_to_px],
            [px_offset +5.2*m_to_px + 1*m_to_px, px_offset +0.8*m_to_px + 0.64* 0.9*m_to_px],
            [px_offset +5.2*m_to_px + 1.1*m_to_px, px_offset +0.8*m_to_px + 0.64* 1.3*m_to_px],
            [px_offset +5.2*m_to_px + 1.2*m_to_px, px_offset +0.8*m_to_px + 0.64* 1.9*m_to_px],
            [px_offset +5.2*m_to_px + 1.2*m_to_px, px_offset +0.8*m_to_px + 0.64* 2.5*m_to_px],
            [px_offset +5.2*m_to_px + 1.2*m_to_px, px_offset +0.8*m_to_px + 0.64* 2.8*m_to_px],
            [px_offset +5.2*m_to_px + 1.1*m_to_px, px_offset +0.8*m_to_px + 0.64* 3.4*m_to_px],
            [px_offset +5.2*m_to_px + 1*m_to_px, px_offset +0.8*m_to_px + 0.64* 3.8*m_to_px],
            [px_offset +5.2*m_to_px + 0.9*m_to_px, px_offset +0.8*m_to_px + 0.64* 4*m_to_px],
            [px_offset +5.2*m_to_px + 0.8*m_to_px, px_offset +0.8*m_to_px + 0.64* 4.2*m_to_px],
            [px_offset +5.2*m_to_px + 0.5*m_to_px, px_offset +0.8*m_to_px + 0.64* 4.4*m_to_px],
            [px_offset +5.2*m_to_px + 0.3*m_to_px, px_offset +0.8*m_to_px + 0.64* 4.5*m_to_px],
            
            [px_offset +5.2*m_to_px, px_offset + 3.7*m_to_px],
            [px_offset +1.2*m_to_px, px_offset + 3.7*m_to_px],
            
            
            [px_offset + 1.2*m_to_px - 0.3*m_to_px, px_offset +0.8*m_to_px + 0.64* 4.5*m_to_px],
            [px_offset + 1.2*m_to_px - 0.5*m_to_px, px_offset +0.8*m_to_px + 0.64* 4.4*m_to_px],
            [px_offset + 1.2*m_to_px - 0.8*m_to_px, px_offset +0.8*m_to_px + 0.64* 4.2*m_to_px],
            [px_offset + 1.2*m_to_px - 0.9*m_to_px, px_offset +0.8*m_to_px + 0.64* 4*m_to_px],
            [px_offset + 1.2*m_to_px - 1*m_to_px, px_offset +0.8*m_to_px + 0.64* 3.8*m_to_px],
            [px_offset + 1.2*m_to_px - 1.1*m_to_px, px_offset +0.8*m_to_px + 0.64* 3.4*m_to_px],
            [px_offset + 1.2*m_to_px - 1.2*m_to_px, px_offset +0.8*m_to_px + 0.64* 2.8*m_to_px],
            [px_offset + 1.2*m_to_px - 1.2*m_to_px, px_offset +0.8*m_to_px + 0.64* 2.5*m_to_px],
            [px_offset + 1.2*m_to_px - 1.2*m_to_px, px_offset +0.8*m_to_px + 0.64* 1.9*m_to_px],
            [px_offset + 1.2*m_to_px - 1.1*m_to_px, px_offset +0.8*m_to_px + 0.64* 1.3*m_to_px],
            [px_offset + 1.2*m_to_px - 1*m_to_px, px_offset +0.8*m_to_px + 0.64* 0.9*m_to_px],
            [px_offset + 1.2*m_to_px - 0.9*m_to_px, px_offset +0.8*m_to_px + 0.64* 0.7*m_to_px],
            [px_offset + 1.2*m_to_px - 0.8*m_to_px, px_offset +0.8*m_to_px + 0.64* 0.5*m_to_px],
            [px_offset + 1.2*m_to_px - 0.5*m_to_px, px_offset +0.8*m_to_px + 0.64* 0.25*m_to_px],
            [px_offset + 1.2*m_to_px - 0.3*m_to_px, px_offset +0.8*m_to_px + 0.64* 0.1*m_to_px],
           ],
    middle: [Scene.w / 2, Scene.h / 2],
  
    // check if point is inside of inner boundary
    is_in: function(x, y) {
      let boundary = this.inner;
      let isInside = false;
      let i, j = boundary.length - 1;
  
      for (i = 0; i < boundary.length; i++) {
        if (((boundary[i][1] > y) !== (boundary[j][1] > y)) &&
            (x < (boundary[j][0] - boundary[i][0]) * (y - boundary[i][1]) / (boundary[j][1] - boundary[i][1]) + boundary[i][0])) {
          isInside = !isInside;
        }
        j = i;
      }
  
      return isInside;
    },
  
    // check if point is outside of outer boundary
    is_out: function(x, y) {
      let boundary = this.outer;
      let isInside = false;
      let i, j = boundary.length - 1;
  
      for (i = 0; i < boundary.length; i++) {
        if (((boundary[i][1] > y) !== (boundary[j][1] > y)) &&
            (x < (boundary[j][0] - boundary[i][0]) * (y - boundary[i][1]) / (boundary[j][1] - boundary[i][1]) + boundary[i][0])) {
          isInside = !isInside;
        }
        j = i;
      }
  
      return !isInside;
    },
  
    
    // need to get some kind of clockwise direction for points in the track
    // -> use several intermediate points inside of track to get directions
    // function assumes that the point x,y is inside of track
      get_direction_checkpoint : function(x,y) { // TODO FIXME
      if (x < px_offset +1.2*m_to_px) {
        return [px_offset +1.2*m_to_px, px_offset + 0.8*m_to_px] // TOP LEFT
      } else if (y < px_offset + 0.8*m_to_px && x < px_offset +5.2*m_to_px) {
            return [px_offset +5.2*m_to_px, px_offset + 0.8*m_to_px] // TOP RIGHT    
       } else if(x > px_offset +5.2*m_to_px) {
         return [px_offset +5.2*m_to_px, px_offset + 3.7*m_to_px] // BOTTOM RIGHT
       } else if (y > px_offset + 3.7*m_to_px) {
         return [px_offset +1.2*m_to_px, px_offset + 3.7*m_to_px] // BOTTOM LEFT
        }
    }
  
  }
  
  class Particle {
    constructor() {
      this.pos = createVector(random(0, Scene.w), random(0, Scene.h))
      this.dir = p5.Vector.random2D()
    }
  
    step() {
      let N=0, avg_sin = 0, avg_cos = 0, avg_p = createVector(0, 0), avg_d = createVector(0, 0)
  
      // compute average angle and average position
      // avg angle for allignment, avg pos for cohesion
      for (let n of Scene.neighbours(this.pos)) {
        avg_p.add(n.pos)
  
        // separation
        if (n != this) {
          let away = p5.Vector.sub(this.pos, n.pos)
          away.div(away.magSq())
          avg_d.add(away)
        }
  
        avg_sin += Math.sin(n.dir.heading())
        avg_cos += Math.cos(n.dir.heading())
        N++
      }
      avg_sin /= N, avg_cos /= N, avg_p.div(N), avg_d.div(N)
      let avg_angle = Math.atan2(avg_sin, avg_cos)
      // add some random noise to the angle
      avg_angle += random(-0.25, 0.25)
      this.dir = p5.Vector.fromAngle(avg_angle)
  
      // implement the cohesion
      let cohesion = p5.Vector.sub(avg_p, this.pos)
      cohesion.div(20)
      this.dir.add(cohesion)
  
      // add separation
      avg_d.mult(20)
      this.dir.add(avg_d)
  
      // implement racetrack force
      // TODO: check and make changes if needed
      let mid_vec = createVector(racetrack.middle[0], racetrack.middle[1])
      if (racetrack.is_in(this.pos.x, this.pos.y)) {
        // if particle is inside inner boundary, make it move in direction away from the middle
  
        this.dir = createVector(0, 0) // first null the current direction, as it goes out of track
  
        // compute vector from current position to mid, and "normalize" it by its magnitude
        let vec_from_pos_to_mid = mid_vec.sub(this.pos)
        vec_from_pos_to_mid.div(vec_from_pos_to_mid.mag())
        
        this.dir.sub(vec_from_pos_to_mid)
      } else if (racetrack.is_out(this.pos.x, this.pos.y)) {
        // if it is in the outer part, make it move in direction to the origin
  
        this.dir = createVector(0, 0) // first null the current direction, as it goes out of track
  
        // compute vector from current position to mid, and "normalize" it by its magnitude
        let vec_from_pos_to_mid = mid_vec.sub(this.pos)
        vec_from_pos_to_mid.div(vec_from_pos_to_mid.mag())
  
        this.dir.add(vec_from_pos_to_mid)
      } else {
        // if particle is in the track, compute a direction to continue moving (clockwise)
  
        // compute vector from current position to next checkpoint on the track
        let next_checkpoint = racetrack.get_direction_checkpoint(this.pos.x, this.pos.y)
        let next_checkpoint_vec = createVector(next_checkpoint[0], next_checkpoint[1])
        let vec_from_pos_to_next_checkpoint = next_checkpoint_vec.sub(this.pos)
        vec_from_pos_to_next_checkpoint.div(vec_from_pos_to_next_checkpoint.magSq()) // "normalize" it by its magnitude
  
        this.dir.add(vec_from_pos_to_next_checkpoint)
      }
  
      this.pos.add(this.dir)
      Scene.wrap(this.pos)
    }
  
    draw() {
      fill(0)
      ellipse(this.pos.x, this.pos.y, 10, 10)
    }
  }
  
  function setup() {
    createCanvas(Scene.w, Scene.h);
    display_racetrack();
  
    // generate particles
    for (let i = 0; i < 100; i++) {
      Scene.swarm.push(new Particle())
    }
  }
  
  function draw() {
    clear()
    display_racetrack() // always display racetrack after clear
    let i = 0
    for (let p of Scene.swarm) {
      // TODO: update logging depending on needs
      // console.log(i, p.pos.x, p.pos.y)
      p.step()
      p.draw()
      i++
    }
  }
  
  // draw simple line from begin to end
  function drawLine(ctx, begin, end, stroke = 'green', width = 1) {
    ctx.strokeStyle = stroke;
    ctx.lineWidth = width;
  
    ctx.beginPath();
    ctx.moveTo(...begin);
    ctx.lineTo(...end);
    ctx.stroke();
  }
  
  // display simplified race track
  function display_racetrack() {
    const canvas = document.querySelector('canvas');
    const ctx = canvas.getContext('2d');
  
    // save all original attributes so that we dont loose them 
    let original_strokeStyle = ctx.strokeStyle;
    let original_lineWidth = ctx.lineWidth;
    let original_lineJoin = ctx.lineJoin;
    let original_lineCap = ctx.lineCap;
  
    ctx.lineJoin = 'circular';
    ctx.lineCap = 'circular';
  
    // draw the inner and outer track
    let len = racetrack.inner.length
    for (let i = 0; i < len; i++) {
      drawLine(ctx, racetrack.inner[i], racetrack.inner[(i+1) % len], 'green', 10);
    }
    len = racetrack.outer.length
    for (let i = 0; i < len; i++) {
      drawLine(ctx, racetrack.outer[i], racetrack.outer[(i+1) % len], 'green', 10);
    }
  
    // assign back the original values 
    ctx.strokeStyle = original_strokeStyle;
    ctx.lineWidth = original_lineWidth;
    ctx.lineJoin = original_lineJoin;
    ctx.lineCap = original_lineCap;
  };
  