/**
 * Path object
 *
 * @name Path
 * @constructor
 *
 * @property {Array} points A list of path points
 * @property {Number} radius Path radius
 */

var Path = function() {
  'use strict';

  this.points = [];
  this.radius = 0;
  this.radius_vertical = 0;
  this.radius_horizontal = 0;

  /**
   * Add a point to path
   *
   * @function
   * @memberOf Path
   *
   * @param {Number} x X coordinate of the path point
   * @param {Number} y Y coordinate of the path point
   */
  this.addPoint = function (x, y) {
    var point = vec2.fromValues(x, y);

    this.points.push(point);
  };

  /**
   * Render path
   *
   * @function
   * @memberOf Path
   */
  this.display = function() {
    ctx.lineJoin = 'round';
    ctx.lineCap = 'round';
    ctx.strokeStyle = '#e7e7e7';
    ctx.lineWidth = this.radius * 2;

    ctx.beginPath();  
    ctx.lineWidth = this.radius;
    ctx.moveTo(this.points[0][0], this.points[0][1]);
    ctx.lineWidth = this.radius;
    ctx.lineTo(this.points[1][0], this.points[1][1]);
    // ctx.stroke();
    ctx.lineWidth = this.radius * 2;
    ctx.lineTo(this.points[2][0], this.points[2][1]);
    ctx.stroke();
    ctx.lineWidth = this.radius;
    ctx.lineTo(this.points[3][0], this.points[3][1]);
    // ctx.lineWidth = this.radius;
    //     ctx.lineTo(this.points[1][0], this.points[1][1]);
    // ctx.lineTo(this.points[2][0], this.points[2][1]);
    // for (var i = 0; i < this.points.length; i++) {
    //   ctx.lineTo(this.points[i][0], this.points[i][1]);
    // }
    ctx.closePath();

    // ctx.beginPath();
    // ctx.lineTo(this.points[1][0], this.points[1][1]);
    // ctx.lineTo(this.points[2][0], this.points[2][1]);
    // ctx.closePath();

    // ctx.lineWidth = this.radius_horizontal * 2;
    // ctx.beginPath();
    // // for (var i = 0; i < this.points.length; i++) {
    // //   ctx.lineTo(this.points[i][0], this.points[i][1]);
    // // }
    // ctx.closePath();

    ctx.stroke();
  };
};
