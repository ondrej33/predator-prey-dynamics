#include <iostream>
#include <vector>
#include <cmath>
#include <memory>
#include <ctime>
#include <nlohmann/json.hpp>
#include <random>
#include <fstream>
#include "glm/glm/glm.hpp"
#include "glm/glm/gtx/norm.hpp"


// define constants
const int WIDTH = 800;
const int HEIGHT = 600;

using namespace std;


glm::vec2 getRandomPlace(int mapWidth, int mapHeight) {
    return {(float)(rand() % mapWidth), (float)(rand() % mapHeight)};
}

glm::vec2 getRandomDirection() {
    return {(float)(1 - 2*(rand()%2)) * (float) (rand() % 1000000) / 1000000,
            (float)(1 - 2*(rand()%2)) * (float) (rand() % 1000000) / 1000000};
}

glm::vec2 getNearestBorderPoint(glm::vec2 fishPosition, int canvasWidth, int canvasHeight) {
    glm::vec2 nearestPoint;

    // Find the closest border to the fish
    float leftDist = fishPosition.x;
    float rightDist = canvasWidth - fishPosition.x;
    float topDist = fishPosition.y;
    float bottomDist = canvasHeight - fishPosition.y;

    float minDist = std::min({leftDist, rightDist, topDist, bottomDist});

    // Calculate the nearest point on the border
    if (minDist == leftDist) {
        nearestPoint = glm::vec2(0.0f, fishPosition.y);
    } else if (minDist == rightDist) {
        nearestPoint = glm::vec2(canvasWidth, fishPosition.y);
    } else if (minDist == topDist) {
        nearestPoint = glm::vec2(fishPosition.x, 0.0f);
    } else if (minDist == bottomDist) {
        nearestPoint = glm::vec2(fishPosition.x, canvasHeight);
    }

    return nearestPoint;
}

bool isFishOutOfBorders(glm::vec2 fishPosition, int canvasWidth, int canvasHeight) {
    if (fishPosition.x < 0 || fishPosition.x > canvasWidth || fishPosition.y < 0 || fishPosition.y > canvasHeight) {
        return true;
    }

    return false;
}

class Fish {
public:
    // first Width, then Height
    glm::vec2 pos;
    glm::vec2 dir;
    int id;
    bool alive=true;

    Fish(int id) {
        this->id = id;
        this->pos = getRandomPlace(WIDTH, HEIGHT);
        this->dir = getRandomDirection();
    }

    void step(vector<Fish> & neighbours, const vector<glm::vec2>& sharks_pos, int fish_sense_dist, bool wall, float fish_max_speed) {
        // when is dead, do nothing
        if (!alive)
            return;

        int N = 0;
        float avg_sin = 0, avg_cos = 0;
        glm::vec2 avg_p(0), avg_d(0);

        // compute average angle and average position
        // avg angle for alignment, avg pos for cohesion
        for (auto n : neighbours) {
            avg_p += n.pos;

            // separation
            if (n.id != this->id) {
                glm::vec2 away = this->pos - n.pos;
                away /= glm::length2(away);
                avg_d += away;
            }

            // calculate the heading angle of the vector in the xy-plane
            float angle = glm::atan(n.dir[1], n.dir[0]);

            avg_sin += sin(angle);
            avg_cos += cos(angle);
            N++;
        }

        // divide everything by N (we want average values)
        avg_sin /= (float)N, avg_cos /= (float)N, avg_p /= N, avg_d /= N;

        float avg_angle = atan2(avg_sin, avg_cos);

        // add some random noise to the angle
        std::mt19937 rng;
        std::uniform_real_distribution<float> dist(-0.01, 0.01);
        float noise = dist(rng);
        avg_angle += noise;

        this->dir = glm::vec2(cos(avg_angle), sin(avg_angle));

        // implement the cohesion
        glm::vec2 cohesion = avg_p - this->pos;
        cohesion /= 20;
        this->dir += cohesion;

        // add separation
        avg_d *= 20;
        this->dir += avg_d;

        // repulse from each shark
        for (auto & shark_pos: sharks_pos) {
            // add repulsive force from shark if it is near the fish
            if (glm::distance(shark_pos, this->pos) <= (float) fish_sense_dist) {
                glm::vec2 shark_repulsion_vec = this->pos - shark_pos;
                shark_repulsion_vec /= glm::length(shark_repulsion_vec); // normalize
                // shark_repulsion_vec = glm::normalize(shark_repulsion_vec); // normalize
                shark_repulsion_vec *= 10;
                this->dir += shark_repulsion_vec;
            }
        }

        // handle wall
        if (wall) {
            // add wall repulsion vector
            glm::vec2 nearest_wall = getNearestBorderPoint(this->pos, WIDTH, HEIGHT);
            if (glm::distance(nearest_wall, this->pos) <= (float)fish_sense_dist) {
                glm::vec2 wall_repulsion_vector = this->pos - nearest_wall;
                wall_repulsion_vector /= glm::length(wall_repulsion_vector); // normalize
                //    wall_repulsion_vector = glm::normalize(wall_repulsion_vector); // normalize
                // wall_repulsion_vector *= 10;
                this->dir += wall_repulsion_vector;
            }

            // cant go trough wall
            if (isFishOutOfBorders(this->pos + this->dir, WIDTH, HEIGHT))
//                this->dir = {-this->dir[1], this->dir[0]};
                this->dir *= -1;
        }

        // handle max speed of a fish
//        float fish_max_speed = 6;
        if (glm::length(this->dir) > fish_max_speed)
            this->dir /= (glm::length(this->dir) / fish_max_speed);

        // update fish position
        this->pos += this->dir;
    }
};


class Shark {
public:
    // first Width, then Height
    glm::vec2 pos;
    glm::vec2 dir;
    int id;
    int kill_radius;

    Shark(int id, int shark_kill_radius) {
        this->id = id;
        this->kill_radius = shark_kill_radius;
        this->pos = getRandomPlace(WIDTH, HEIGHT);
        this->dir = getRandomDirection();
    };

    void step(vector<Fish> & neighbours, bool wall, int shark_max_speed, int shark_sense_dist) {
        int N = 0;
        auto avg_p = glm::vec2(0.0f);

        // compute the average position of neighbouring fish
        for (Fish n : neighbours) {
            avg_p += n.pos;
            N++;
        }

        if (N == 0) {
            // if no neighbours, shift randomly for a bit
            std::random_device rd;
            std::mt19937 gen(rd());
            std::uniform_real_distribution<float> dis(-0.5f, 0.5f);
            float avg_angle = dis(gen);
            this->dir = glm::vec2(cos(avg_angle), sin(avg_angle));
        } else {
            // otherwise go for the average position of neighbouring fish
            avg_p /= static_cast<float>(N);
            glm::vec2 hunt_vector = avg_p - this->pos;
            hunt_vector = glm::normalize(hunt_vector);// normalize by its squared length
            this->dir += hunt_vector;
        }

        // add wall behaviour
        if (wall) {
            // add wall repulsion vector
            glm::vec2 nearest_wall = getNearestBorderPoint(this->pos, WIDTH, HEIGHT);
            if (glm::distance(nearest_wall, this->pos) <= (float)shark_sense_dist) {
                glm::vec2 wall_repulsion_vec = this->pos - nearest_wall;
                wall_repulsion_vec /= glm::length(wall_repulsion_vec); // normalize
                //    wall_repulsion_vec = glm::normalize(wall_repulsion_vec); // normalize
//                 wall_repulsion_vec *= 10;
                this->dir += wall_repulsion_vec;
            }

            // cant go trough wall
            if (isFishOutOfBorders(this->pos + this->dir, WIDTH, HEIGHT))
//                this->dir = {-this->dir[1], this->dir[0]};
                this->dir *= -1;
        }


        // handle max speed of a shark
        if (glm::length(this->dir) > (float)5)
            this->dir /= (glm::length(this->dir) / (float)5);

        // update position
        this->pos += this->dir;
    }
};


class Scene {
private:
    int width;
    int height;
    int num_fish;
    int num_sharks;
    vector<Fish> swarm;
    vector<Shark> sharks;
    int fish_sense_dist; // distance for fish senses
    int shark_sense_dist; // distance for shark senses
    int shark_kill_radius;
    int shark_max_speed;
    float fish_max_speed;
    bool wall;

public:
    Scene(int width, int height, int num_fish, int fish_sense_dist, int shark_sense_dist, int num_sharks,
          bool wall, int shark_kill_radius, int shark_max_speed, float fish_max_speed) {
        this->width = width;
        this->height = height;
        this->num_fish = num_fish;
        this->num_sharks = num_sharks;
        this->fish_sense_dist = fish_sense_dist;
        this->shark_sense_dist = shark_sense_dist;
        this->wall = wall;
        this->shark_kill_radius = shark_kill_radius;
        this->shark_max_speed = shark_max_speed;
        this->fish_max_speed = fish_max_speed;

        // generate fish
        for (int i=0; i < this->num_fish; i ++) {
            swarm.emplace_back(Fish(i));
        }

        // generate sharks
        for (int i = 0; i < this->num_sharks; i++)
            sharks.emplace_back(Shark(i, this->shark_kill_radius));
    }

    // get neighbors for prey fish up to certain distance
    vector<Fish> getFishNeighbours(Fish fish) {
        vector<Fish> neighbours;

        for (auto f: swarm){
            if (f.alive && glm::distance(fish.pos, f.pos)<= (float)this->fish_sense_dist) {
                neighbours.push_back(f);
            }
        }

        return neighbours;
    }

    // get neighbors for predator shark up to certain distance
    vector<Fish> getFishPrey(const Shark& s) {
        vector<Fish> neighbours;

        for (const auto& f: swarm){
            if (f.alive && glm::distance(s.pos, f.pos)<= (float)this->shark_sense_dist) {
                neighbours.push_back(f);
            }
        }

        return neighbours;
    }

    // general function to get neighbours up to certain distance
    vector<Fish> getEatenFish(const Shark& s) {
        vector<Fish> eatenFish;

        for (auto& f: swarm) {
            if (f.alive && glm::distance(s.pos, f.pos) <= (float)s.kill_radius) {
                eatenFish.push_back(f);
                f.alive = false;
            }
        }

        return eatenFish;
    }

    // Add outer boundaries of the canvas
    // we use "cyclic" boundaries for now
    void wrap(float& x, float& y) {
        if (x < 0) x += this->width;
        if (y < 0) y += this->height;
        if (x >= this->width) x -= this->width;
        if (y >= this->height) y -= this->height;
    }

    void simulate(int steps, const string& output_filepath) {
        nlohmann::json log;
        vector<nlohmann::json> steps_j;

        for (int i = 0; i < steps; i++){
            std::cout << "step #" << i << endl;

            // move fish
            for (auto& f: swarm) {
                vector<Fish> neighbours = getFishNeighbours(f);
                vector<glm::vec2> sharks_position;
                std::transform(sharks.begin(), sharks.end(), std::back_inserter(sharks_position), [](const Shark s){
                    return s.pos;
                });
                f.step(neighbours, sharks_position, this->fish_sense_dist, this->wall, this->fish_max_speed);
                wrap(f.pos[0], f.pos[1]);
            }

            // handle sharks
            for (auto &s: this->sharks) {
                // move shark
                vector<Fish> prey_neighbours = getFishPrey(s);
                s.step(prey_neighbours, this->wall, this->shark_max_speed, this->shark_sense_dist);
                wrap(s.pos[0], s.pos[1]);

                // label eaten fish
                vector<Fish> eatenFish = getEatenFish(s);
            }

            steps_j.push_back(logStepToJson());
        }

        // complete json object
        log = {
                {"scene", {
                                  {"width", WIDTH},
                                  {"height", HEIGHT}
                          }},
                {"steps", steps_j}
        };

        // save log to json file
        std::ofstream file(output_filepath);
        file << log.dump(-1);
        file.close();
    }

    nlohmann::json logStepToJson() {
        // create an empty JSON object
        nlohmann::json j;

        // create json object to each fish
        vector<nlohmann::json> swarm_j;
        for (auto & f: this->swarm) {
            nlohmann::json fish_j;
            fish_j = {
                    {"id", f.id},
                    {"x", (int)f.pos[0]},
                    {"y", (int)f.pos[1]},
                    {"alive", f.alive}
            };
            swarm_j.emplace_back(fish_j);
        }

        // create json object to each shark
        vector<nlohmann::json> sharks_j;
        for (auto &s: this->sharks) {
            nlohmann::json shark_j;
            shark_j = {
                    {"id", s.id},
                    {"x", (int)s.pos[0]},
                    {"y", (int)s.pos[1]}
            };
            sharks_j.emplace_back(shark_j);
        }

        // add each attribute to the JSON object
        j = {
                {"sharks", sharks_j},
                {"swarm", swarm_j}
        };

        return j;
    }
};

int main(int argc, char ** argv) {
    // SET VARIABLES
    const int num_fish = 500,
            fish_sense_dist = 30,
            shark_sense_dist = 50,
            shark_kill_radius = 20,
            num_steps = 2000,
            num_sharks = 3,
            shark_max_speed = 5,
            fish_max_speed = 5;
    bool wall = true;
    const string output_filepath = "output.json";

    // =============================

    std::cout << "Simulation starts:" << std::endl;

    // Start measuring time
    std::clock_t start = std::clock();

    // setup Scene
    shared_ptr<Scene> scene = make_shared<Scene>(WIDTH,
                                                 HEIGHT,
                                                 num_fish,
                                                 fish_sense_dist,
                                                 shark_sense_dist,
                                                 num_sharks,
                                                 wall,
                                                 shark_kill_radius,
                                                 shark_max_speed,
                                                 fish_max_speed);

    // simulation
    scene->simulate(num_steps, output_filepath);

    // Stop measuring time
    std::clock_t end = std::clock();

    // Calculate the elapsed time in seconds
    double elapsed_time = static_cast<double>(end - start) / CLOCKS_PER_SEC;

    // Print the elapsed time
    std::cout << "Simulation ends" << std::endl;
    std::cout << "Elapsed time: " << elapsed_time << " seconds." << std::endl;

    return 0;
}
