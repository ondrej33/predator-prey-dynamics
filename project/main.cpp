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
#include <boost/program_options.hpp>


using namespace std;

// define scene constants
const int WIDTH = 600;
const int HEIGHT = 600;

// define MODEL PARAMETERS - constants to multiply various forces
// these (their subset) can be used for parameter optimisation
float FISH_MOMENTUM_CONSTANT = 0.75;
float SHARK_MOMENTUM_CONSTANT = 1.;
float ALIGNMENT_CONSTANT = 0.2;
float COHESION_CONSTANT = 0.05;
float SEPARATION_CONSTANT = 20.;
float SHARK_REPULSION_CONSTANT = 10.;
float HUNT_CONSTANT = 0.5;

bool help=false;


void parse_arguments(int argc, char** argv) {
    // Define the command line options
    boost::program_options::options_description desc("Allowed options");
    desc.add_options()
        ("help", "prints help")
        ("fish-momentum", boost::program_options::value<float>(&FISH_MOMENTUM_CONSTANT), "Momentum constant for fish")
        ("shark-momentum", boost::program_options::value<float>(&SHARK_MOMENTUM_CONSTANT), "Momentum constant for sharks")
        ("alignment", boost::program_options::value<float>(&ALIGNMENT_CONSTANT), "Alignment constant")
        ("cohesion", boost::program_options::value<float>(&COHESION_CONSTANT), "Cohesion constant")
        ("separation", boost::program_options::value<float>(&SEPARATION_CONSTANT), "Separation constant")
        ("shark-repulsion", boost::program_options::value<float>(&SHARK_REPULSION_CONSTANT), "Shark repulsion constant")
        ("hunt", boost::program_options::value<float>(&HUNT_CONSTANT), "Hunt constant");


    // Parse the command line arguments
    boost::program_options::variables_map vm;
    boost::program_options::store(boost::program_options::parse_command_line(argc, argv, desc), vm);
    boost::program_options::notify(vm);

    // Print usage message for all options when the help option is provided
    if (vm.count("help")) {
        std::cout << desc << std::endl;
        help = true;
    }
}

glm::vec2 getRandomPlace(int mapWidth, int mapHeight) {
    return {(float)(rand() % mapWidth), (float)(rand() % mapHeight)};
}

glm::vec2 getRandomDirection() {
    return {(float)(1 - 2 * (rand() % 2)) * (float) (rand() % 1000000) / 1000000,
            (float)(1 - 2 * (rand() % 2)) * (float) (rand() % 1000000) / 1000000};
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
    return (fishPosition.x < 0 || fishPosition.x > canvasWidth || fishPosition.y < 0 || fishPosition.y > canvasHeight);
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
        // when it is dead, do nothing
        if (!alive)
            return;


        // compute average angle, average position and average distance from neighbours
        // avg angle for alignment, avg pos for cohesion, avg dist for separation

        int N = 0;
        float avg_sin = 0, avg_cos = 0;
        glm::vec2 avg_p(0), avg_d(0);
        for (auto n : neighbours) {
            avg_p += n.pos;

            // separation computation
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

        // get angle from sin cos values
        float avg_angle = atan2(avg_sin, avg_cos);
        // add some random noise to the direction angle
        std::mt19937 rng;
        std::uniform_real_distribution<float> dist(-0.01, 0.01);
        float noise = dist(rng);
        avg_angle += noise;

        // momentum - consider previous direction as a base to add the forces
        this->dir = this->dir * FISH_MOMENTUM_CONSTANT;

        // alignment force
        glm::vec2 allignment_vec = glm::vec2(cos(avg_angle), sin(avg_angle));
        allignment_vec *= ALIGNMENT_CONSTANT;
        this->dir += allignment_vec;

        // cohesion force
        glm::vec2 cohesion_vec = avg_p - this->pos;
        cohesion_vec *= COHESION_CONSTANT;
        this->dir += cohesion_vec;

        // separation force
        glm::vec2 separation_vec = avg_d;
        separation_vec *= SEPARATION_CONSTANT;
        this->dir += separation_vec;

        // repulse force from each shark
        for (auto & shark_pos: sharks_pos) {
            // add repulsive force from shark if it is near the fish
            if (glm::distance(shark_pos, this->pos) <= (float) fish_sense_dist) {
                glm::vec2 shark_repulsion_vec = this->pos - shark_pos;
                shark_repulsion_vec /= glm::length(shark_repulsion_vec); // divide by magnitude
                shark_repulsion_vec *= SHARK_REPULSION_CONSTANT;
                this->dir += shark_repulsion_vec;
            }
        }

        // wall repulsion, if it is enabled
        if (wall) {
            // add wall repulsion vector (from the nearest wall point)
            glm::vec2 nearest_wall = getNearestBorderPoint(this->pos, WIDTH, HEIGHT);
            if (glm::distance(nearest_wall, this->pos) <= (float)fish_sense_dist) {
                glm::vec2 wall_repulsion_vector = this->pos - nearest_wall;
                wall_repulsion_vector /= glm::length(wall_repulsion_vector); // divide by its magnitude
                wall_repulsion_vector *= 2; // make it bit larger to avoid clustering in corners
                this->dir += wall_repulsion_vector;
            }

            // cant go through the wall
            if (isFishOutOfBorders(this->pos + this->dir, WIDTH, HEIGHT)) {
                this->dir *= -1;
            }
        }

        // check if fish does not exceed its max speed
        if (glm::length(this->dir) > fish_max_speed) {
            this->dir /= (glm::length(this->dir) / fish_max_speed);
        }

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

        // compute the average position of neighbouring fish
        int N = 0;
        auto avg_p = glm::vec2(0.0f);
        for (Fish n : neighbours) {
            avg_p += n.pos;
            N++;
        }

        // momentum - consider previous direction as a base to add the forces to
        this->dir = this->dir * SHARK_MOMENTUM_CONSTANT;

        if (N == 0) {
            // if no neighbours, shift randomly for a bit
            std::random_device rd;
            std::mt19937 gen(rd());
            std::uniform_real_distribution<float> dis(-0.5f, 0.5f);
            float avg_angle = dis(gen);
            auto random_vec = glm::vec2(cos(avg_angle), sin(avg_angle));
            this->dir += random_vec;
        } else {
            // otherwise go for the average position of neighbouring fish
            avg_p /= static_cast<float>(N);
            glm::vec2 hunt_vector = avg_p - this->pos;
            hunt_vector /= glm::length2(hunt_vector); // divide by it magnitude
            hunt_vector *= HUNT_CONSTANT;
            this->dir += hunt_vector;
        }

        // wall repulsion, if it is enabled
        if (wall) {
            // add wall repulsion vector
            glm::vec2 nearest_wall = getNearestBorderPoint(this->pos, WIDTH, HEIGHT);
            if (glm::distance(nearest_wall, this->pos) <= (float)shark_sense_dist) {
                glm::vec2 wall_repulsion_vec = this->pos - nearest_wall;
                wall_repulsion_vec /= glm::length(wall_repulsion_vec); // divide by its magnitude
                wall_repulsion_vec *= 2;
                this->dir += wall_repulsion_vec;
            }

            // cant go trough wall
            if (isFishOutOfBorders(this->pos + this->dir, WIDTH, HEIGHT)) {
                this->dir *= -1;
            }
        }

        // ensure max speed of a shark
        if (glm::length(this->dir) > shark_max_speed) {
            this->dir /= (glm::length(this->dir) / shark_max_speed);
        }

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
    int num_steps;

public:
    Scene(int width, int height, int num_fish, int fish_sense_dist, int shark_sense_dist, int num_sharks,
          bool wall, int shark_kill_radius, int shark_max_speed, float fish_max_speed, int num_steps) {
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
        this->num_steps = num_steps;

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

    // mark eaten fish as dead and return them
    vector<Fish> getEatenFish(const Shark& s) {
        vector<Fish> eatenFish;
        for (auto& f: swarm) {
            if (f.alive && glm::distance(s.pos, f.pos) <= (float)s.kill_radius) {
                f.alive = false;
                eatenFish.push_back(f);
            }
        }
        return eatenFish;
    }

    // FUnction to wrap outer boundaries of the canvas using "cyclic" boundaries
    void wrap(float& x, float& y) {
        if (x < 0) x += this->width;
        if (y < 0) y += this->height;
        if (x >= this->width) x -= this->width;
        if (y >= this->height) y -= this->height;
    }

    void simulate(int steps, const string& output_filepath, bool debug) {
        nlohmann::json log;
        vector<nlohmann::json> steps_j;
        size_t fish_eaten_total = 0;

        for (int i = 0; i < steps; i++){
            if (debug) std::cout << "step #" << i;

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
            size_t eaten_fish_counter = 0;
            for (auto &s: this->sharks) {
                // move shark
                vector<Fish> prey_neighbours = getFishPrey(s);
                s.step(prey_neighbours, this->wall, this->shark_max_speed, this->shark_sense_dist);
                wrap(s.pos[0], s.pos[1]);

                // label and count eaten fish
                vector<Fish> eaten_fish = getEatenFish(s);
                eaten_fish_counter += eaten_fish.size();
            }
            if (eaten_fish_counter > 0) {
                if (debug) std::cout << " [" << eaten_fish_counter << " fish eaten]" << endl;
                fish_eaten_total += eaten_fish_counter;
            } else {
                if (debug) std::cout << endl;
            }
            if (debug) steps_j.push_back(logStepToJson());
        }

        // always print this
        std::cout << "TOTAL FISH EATEN: " << fish_eaten_total << endl;

        if (debug) {
            // complete json object
            log = {
                {"scene",
                    {
                        {"width", WIDTH},
                        {"height", HEIGHT}
                    }
                },
                {"stepsTotal", this->num_steps},
                {"steps", steps_j}
            };

            // save log to json file -- must not forget to delete previous content
            std::ofstream file(output_filepath, std::ofstream::out | std::ofstream::trunc);
            file << log.dump(-1);
            file.close();
        }
    }

    nlohmann::json logStepToJson() {
        // create an empty JSON object
        nlohmann::json j;

        // create json object to each fish
        vector<nlohmann::json> swarm_j;
        for (auto & f: this->swarm) {
            nlohmann::json fish_j;
            float direction_radians = atan2(f.dir[0], f.dir[1]);
            fish_j = {
                    {"id", f.id},
                    {"x", (int)f.pos[0]},
                    {"y", (int)f.pos[1]},
                    {"dir", direction_radians},
                    {"alive", f.alive}
            };
            swarm_j.emplace_back(fish_j);
        }

        // create json object to each shark
        vector<nlohmann::json> sharks_j;
        for (auto &s: this->sharks) {
            nlohmann::json shark_j;
            float direction_radians = atan2(s.dir[0], s.dir[1]);
            shark_j = {
                    {"id", s.id},
                    {"x", s.pos[0]},
                    {"y", s.pos[1]},
                    {"dir", direction_radians},
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

int main(int argc, char** argv) {
    // as constants at the beginning
    parse_arguments(argc, argv);

    // if help was printed, end program
    if (help)
        return 0;

    // set SCENE variables
    const int num_fish = 750,
            fish_sense_dist = 25,
            shark_sense_dist = 50,
            shark_kill_radius = 15,
            num_steps = 2000,
            num_sharks = 3,
            shark_max_speed = 6,
            fish_max_speed = 5;

    bool debug = true; // this enables printing + logging to json
    bool wall = true;
    const string output_filepath = "output.json";

    // =============================

    std::cout << "Simulation starts." << std::endl;

    // Start measuring time
    std::clock_t start = std::clock();

    // setup Scene
    shared_ptr<Scene> scene = make_shared<Scene>(
        WIDTH,
        HEIGHT,
        num_fish,
        fish_sense_dist,
        shark_sense_dist,
        num_sharks,
        wall,
        shark_kill_radius,
        shark_max_speed,
        fish_max_speed,
        num_steps
    );

    // simulation
    scene->simulate(num_steps, output_filepath, debug);

    // Stop measuring time
    std::clock_t end = std::clock();

    // Calculate the elapsed time in seconds
    double elapsed_time = static_cast<double>(end - start) / CLOCKS_PER_SEC;

    // Print the elapsed time
    std::cout << "Simulation ends" << std::endl;
    std::cout << "Elapsed time: " << elapsed_time << " seconds." << std::endl;

    return 0;
}
