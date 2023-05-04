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
#include <unordered_set>


using namespace std;

// We have two types of model parameters:

// 1) OPTIMIZABLE MODEL PARAMETERS - these will be used for parameter optimisation
// their values can be given via CLI arguments
// basically factors to multiply various forces of FISH
float FISH_MOMENTUM_CONSTANT = 0.75;
float ALIGNMENT_CONSTANT = 0.2;
float COHESION_CONSTANT = 0.05;
float SEPARATION_CONSTANT = 20.;
float SHARK_REPULSION_CONSTANT = 10.;

// 2) FIXED MODEL PARAMETERS - similar, but not to be optimized via evolution
// mostly shark parameters, or scene params
constexpr int WIDTH = 400;            // scene width
constexpr int HEIGHT = 400;           // scene height
constexpr int NUM_STEPS = 1000;       // number of steps to simulate
constexpr int NUM_FISH = 400;         // total number of fish
constexpr int NUM_SHARKS = 3;         // number of sharks
constexpr int FISH_SENSE_DIST = 25;   // distance for fish to sense neighbors
constexpr int SHARK_SENSE_DIST = 50;  // distance for shark to sense neighbors
constexpr int FISH_MAX_SPEED = 5;     // maximal speed of fish
constexpr int SHARK_MAX_SPEED = 6;    // maximal speed of sharks
constexpr int SHARK_KILL_RADIUS = 15; // distance for which shark can kill
constexpr float SHARK_MOMENTUM_CONSTANT = 1.;
constexpr float SHARK_SEARCH_CONSTANT = 2.;
constexpr float HUNT_CONSTANT = 1.;
constexpr bool WALL = true;
constexpr int FISH_DIM_ELLIPSE_X = 5;
constexpr int FISH_DIM_ELLIPSE_Y = 9;

// also help/debug parameters to enable help/debug messages or logs
bool debug = true; // this enables printing + logging to json
bool help = false;

void parse_arguments(int argc, char** argv) {
    // Define the command line options
    boost::program_options::options_description desc("Allowed options");
    desc.add_options()
            ("help", "prints help")
            ("debug", boost::program_options::value<bool>(&debug), "Enable prints for progress")
            ("fish-momentum", boost::program_options::value<float>(&FISH_MOMENTUM_CONSTANT), "Momentum constant for fish")
            ("alignment", boost::program_options::value<float>(&ALIGNMENT_CONSTANT), "Alignment constant")
            ("cohesion", boost::program_options::value<float>(&COHESION_CONSTANT), "Cohesion constant")
            ("separation", boost::program_options::value<float>(&SEPARATION_CONSTANT), "Separation constant")
            ("shark-repulsion", boost::program_options::value<float>(&SHARK_REPULSION_CONSTANT), "Shark repulsion constant");

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

template<int canvasWidth, int canvasHeight>
glm::vec2 getRandomPlace() {
    return {(float)(rand() % canvasWidth), (float)(rand() % canvasHeight)};
}

glm::vec2 getRandomDirection() {
    return {(float)(1 - 2 * (rand() % 2)) * (float) (rand() % 1000000) / 1000000,
            (float)(1 - 2 * (rand() % 2)) * (float) (rand() % 1000000) / 1000000};
}

template<int canvasWidth, int canvasHeight>
glm::vec2 getNearestBorderPoint(glm::vec2 fishPosition) {
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

template<int canvasWidth, int canvasHeight>
bool isFishOutOfBorders(glm::vec2 fishPosition) {
    return (fishPosition.x < 0 || fishPosition.x > canvasWidth || fishPosition.y < 0 || fishPosition.y > canvasHeight);
}

// TODO add possible template
float ellipsesOverlapDistance(glm::vec2 center1, glm::vec2 direction1, float width1, float height1, glm::vec2 center2, glm::vec2 direction2, float width2, float height2) {
    // Normalize the direction vectors
    glm::vec2 normDirection1 = glm::normalize(direction1);
    glm::vec2 normDirection2 = glm::normalize(direction2);

    // Calculate the rotation angles for each ellipse
    float rotation1 = glm::degrees(glm::atan(normDirection1.y, normDirection1.x));
    float rotation2 = glm::degrees(glm::atan(normDirection2.y, normDirection2.x));

    // Calculate the rotation matrices for each ellipse
    glm::mat2 rotationMatrix1 = glm::mat2(glm::vec2(glm::cos(glm::radians(rotation1)), glm::sin(glm::radians(rotation1))), glm::vec2(-glm::sin(glm::radians(rotation1)), glm::cos(glm::radians(rotation1))));
    glm::mat2 rotationMatrix2 = glm::mat2(glm::vec2(glm::cos(glm::radians(rotation2)), glm::sin(glm::radians(rotation2))), glm::vec2(-glm::sin(glm::radians(rotation2)), glm::cos(glm::radians(rotation2))));

    // Transform the centers of the ellipses into the coordinate system of ellipse 1
    glm::vec2 center2Transformed = rotationMatrix1 * (center2 - center1);

    // Calculate the distance between the transformed centers of the two ellipses
    float distance = glm::length(center2Transformed);

    // Calculate the radii of each ellipse in the transformed coordinate system
    glm::vec2 radii1 = glm::vec2(width1 / 2.0f, height1 / 2.0f);
    glm::vec2 radii2 = glm::vec2(width2 / 2.0f, height2 / 2.0f);

    // Transform the radii of ellipse 2 into the coordinate system of ellipse 1
    glm::vec2 radii2Transformed = rotationMatrix1 * rotationMatrix2 * radii2;

    // Calculate the sum of the radii in the x and y directions
    glm::vec2 sumRadii = radii1 + radii2Transformed;

    // Calculate the vector from the center of ellipse 1 to the center of ellipse 2 in the transformed coordinate system
    glm::vec2 centerVector = glm::normalize(center2Transformed);

    // Calculate the projection of the sum of the radii onto the center vector
    float overlapDistance = glm::dot(sumRadii, centerVector) - distance;

    return overlapDistance;
}

class Food {
public:
    glm::vec2 pos;
    int id;
    bool eaten=false;

    Food(int id) {
        this->id = id;
        this->pos = getRandomPlace<WIDTH, HEIGHT>();
    }

    // TODO? Do we want moving food??

    friend bool operator< (const Food &left, const Food &right);
};

bool operator< (const Food &left, const Food &right)
{
    return left.id < right.id;
}

template<int fish_sense_dist, int fish_max_speed, bool wall, int fish_dim_ellipse_x, int fish_dim_ellipse_y>
class Fish {
public:
    // first Width, then Height
    glm::vec2 pos;
    glm::vec2 dir;
    int id;
    bool alive=true;

    Fish(int id) {
        this->id = id;
        this->pos = getRandomPlace<WIDTH, HEIGHT>();
        this->dir = getRandomDirection();
    }

    void step(vector<Fish> & neighbours, const vector<glm::vec2>& sharks_pos) {
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
            glm::vec2 nearest_wall = getNearestBorderPoint<WIDTH, HEIGHT>(this->pos);
            if (glm::distance(nearest_wall, this->pos) <= (float)fish_sense_dist) {
                glm::vec2 wall_repulsion_vector = this->pos - nearest_wall;
                wall_repulsion_vector /= glm::length(wall_repulsion_vector); // divide by its magnitude
                wall_repulsion_vector *= 2; // make it bit larger to avoid clustering in corners
                this->dir += wall_repulsion_vector;
            }

            // cant go through the wall
            if (isFishOutOfBorders<WIDTH, HEIGHT>(this->pos + this->dir)) {
                this->dir *= -1;
            }
        }

        // check if fish does not exceed its max speed
        if (glm::length(this->dir) > fish_max_speed) {
            this->dir /= (glm::length(this->dir) / fish_max_speed);
        }

        // check if fish dimensions does not overlap with other fish
        for (auto &n: neighbours){
            float ovrlpDistance = ellipsesOverlapDistance(
                    this->pos, this->dir,(float) fish_dim_ellipse_x, (float) fish_dim_ellipse_y,
                    n.pos, n.dir, (float) fish_dim_ellipse_x, (float) fish_dim_ellipse_y);
            if (ovrlpDistance > 0) {
                // move direction
                this->dir *= -0.5; // FIXME?
            }
        }

        // TODO adjust the change of direction possible and its momentum (magnitude) - scale direction while turning - if significant turn, there is decrease of momentum


        // update fish position
        this->pos += this->dir;
    }
};


template<int shark_sense_dist, int shark_max_speed, int shark_kill_radius,
        int fish_sense_dist, int fish_max_speed, bool wall, int fish_dim_ellipse_x, int fish_dim_ellipse_y>
class Shark {
public:
    using Fish_t = Fish<fish_sense_dist, fish_max_speed, wall, fish_dim_ellipse_x, fish_dim_ellipse_y>;

    // first Width, then Height
    glm::vec2 pos;
    glm::vec2 dir;
    int id;

    Shark(int id) {
        this->id = id;
        this->pos = getRandomPlace<WIDTH, HEIGHT>();
        this->dir = getRandomDirection();
    };

    void step(vector<Fish_t> & neighbours) {

        // compute the average position of neighbouring fish
        int N = 0;
        auto avg_p = glm::vec2(0.0f);
        for (Fish_t n : neighbours) {
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
            random_vec *= SHARK_SEARCH_CONSTANT;
            this->dir += random_vec;
        } else {
            // otherwise go for the average position of neighbouring fish
            avg_p /= static_cast<float>(N);
            glm::vec2 hunt_vector = avg_p - this->pos;
            hunt_vector /= glm::length2(hunt_vector); // divide by its squared magnitude
            hunt_vector *= HUNT_CONSTANT;
            this->dir += hunt_vector;
        }

        // wall repulsion, if it is enabled
        if (wall) {
            // add wall repulsion vector
            glm::vec2 nearest_wall = getNearestBorderPoint<WIDTH, HEIGHT>(this->pos);
            if (glm::distance(nearest_wall, this->pos) <= (float)shark_sense_dist) {
                glm::vec2 wall_repulsion_vec = this->pos - nearest_wall;
                wall_repulsion_vec /= glm::length(wall_repulsion_vec); // divide by its magnitude
                wall_repulsion_vec *= 2;
                this->dir += wall_repulsion_vec;
            }

            // cant go trough wall
            if (isFishOutOfBorders<WIDTH, HEIGHT>(this->pos + this->dir)) {
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


template<int width, int height, int num_steps, int num_fish, int num_sharks,
        int fish_sense_dist, int shark_sense_dist, int shark_kill_radius,
        int fish_max_speed, int shark_max_speed, bool wall, int fish_dim_ellipse_x, int fish_dim_ellipse_y>
class Scene {
private:
    using Fish_t = Fish<fish_sense_dist, fish_max_speed, wall, fish_dim_ellipse_x, fish_dim_ellipse_y>;
    using Shark_t = Shark<shark_sense_dist, shark_max_speed, shark_kill_radius, fish_sense_dist, fish_max_speed, wall, fish_dim_ellipse_x, fish_dim_ellipse_y>;

    vector<Fish_t> swarm;
    vector<Shark_t> sharks;
    set<Food> food;

public:
    Scene() {
        // generate fish
        for (int i=0; i < num_fish; i ++) {
            swarm.emplace_back(Fish_t(i));
        }

        // generate sharks
        for (int i = 0; i < num_sharks; i++)
            sharks.emplace_back(Shark_t(i));

        // generate food
        for (int i = 0; i < 50; i++) // todo redo it to variable parameter
            food.insert(Food(i));
    }

    // get neighbors for prey fish up to certain distance
    vector<Fish_t> getFishNeighbours(Fish_t fish) {
        vector<Fish_t> neighbours;

        for (auto f: swarm){
            if (f.alive && glm::distance(fish.pos, f.pos)<= (float)fish_sense_dist) {
                neighbours.push_back(f);
            }
        }

        return neighbours;
    }

    // get neighbors for predator shark up to certain distance
    vector<Fish_t> getFishPrey(const Shark_t& s) {
        vector<Fish_t> neighbours;

        for (const auto& f: swarm){
            if (f.alive && glm::distance(s.pos, f.pos)<= (float)shark_sense_dist) {
                neighbours.push_back(f);
            }
        }

        return neighbours;
    }

    // mark eaten fish as dead and return them
    vector<Fish_t> getEatenFish(const Shark_t& s) {
        vector<Fish_t> eatenFish;
        for (auto& f: swarm) {
            if (f.alive && glm::distance(s.pos, f.pos) <= (float)shark_kill_radius) {
                f.alive = false;
                eatenFish.push_back(f);
            }
        }
        return eatenFish;
    }

    // Function to wrap outer boundaries of the canvas using "cyclic" boundaries
    // gets a point, returns either same point, or point on opposite side if it "crosses" boundary
    void wrap(float& x, float& y) {
        if (x < 0) x += width;
        if (y < 0) y += height;
        if (x >= width) x -= width;
        if (y >= height) y -= height;
    }

    void simulate(const string& output_filepath) {
        nlohmann::json log;
        vector<nlohmann::json> steps_j;
        size_t fish_eaten_total = 0;

        for (int i = 0; i < num_steps; i++){
            if (debug) std::cout << "step #" << i;

            // move fish
            for (auto& f: swarm) {
                vector<Fish_t> neighbours = getFishNeighbours(f);
                vector<glm::vec2> sharks_position;
                std::transform(sharks.begin(), sharks.end(), std::back_inserter(sharks_position), [](const Shark_t s){
                    return s.pos;
                });
                f.step(neighbours, sharks_position);
                wrap(f.pos[0], f.pos[1]);
            }

            // handle sharks
            size_t eaten_fish_counter = 0;
            for (auto &s: this->sharks) {
                // move shark
                vector<Fish_t> prey_neighbours = getFishPrey(s);
                s.step(prey_neighbours);
                wrap(s.pos[0], s.pos[1]);

                // label and count eaten fish
                vector<Fish_t> eaten_fish = getEatenFish(s);
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
                                           {"width", width},
                                           {"height", height}
                                   }
                    },
                    {"stepsTotal", num_steps},
                    {"fish_dim_x", fish_dim_ellipse_x},
                    {"fish_dim_y", fish_dim_ellipse_y},
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
        int deadFish = 0;
        vector<nlohmann::json> swarm_j;
        for (auto & f: this->swarm) {
            nlohmann::json fish_j;
            float direction_radians = atan2(f.dir[0], f.dir[1]);
            fish_j = {
                    {"id", f.id},
                    {"x", (int)f.pos[0]},
                    {"y", (int)f.pos[1]},
                    {"dir", direction_radians},
                    {"alive", f.alive},
            };
            swarm_j.emplace_back(fish_j);
            
            if (!f.alive)
                deadFish ++;
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

        // create json object for food
        vector<nlohmann::json> food_j;
        for (auto &f: this->food) {
            nlohmann::json f_j;
//            float direction_radians = atan2(s.dir[0], s.dir[1]);
            f_j = {
                    {"id", f.id},
                    {"x", f.pos[0]},
                    {"y", f.pos[1]},
//                    {"dir", direction_radians},
            };
            food_j.emplace_back(f_j);
        }

        // add each attribute to the JSON object
        j = {
                {"sharks", sharks_j},
                {"swarm", swarm_j},
                {"food", food_j},
                {"deadFish", deadFish},
        };

        return j;
    }
};

int main(int argc, char** argv) {
    // as constants at the beginning
    parse_arguments(argc, argv);

    // check if fish sense dist is bigger than dimensions of the fish (represented as ellipse)
    assert(max(FISH_DIM_ELLIPSE_X, FISH_DIM_ELLIPSE_Y) < FISH_SENSE_DIST &&
           "fish sense dist must be bigger than dimensions of the fish (represented as ellipse)");

    // if help was printed, end program
    if (help)
        return 0;

    const string output_filepath = "output.json";

    // =============================

    if (debug) {
        std::cout << "Simulation starts." << std::endl;
    }

    // Start measuring time
    std::clock_t start = std::clock();

    // setup Scene
    Scene scene = Scene<WIDTH, HEIGHT, NUM_STEPS, NUM_FISH, NUM_SHARKS,
            FISH_SENSE_DIST, SHARK_SENSE_DIST, SHARK_KILL_RADIUS,
            FISH_MAX_SPEED, SHARK_MAX_SPEED, WALL, FISH_DIM_ELLIPSE_X, FISH_DIM_ELLIPSE_Y>();

    // simulation
    scene.simulate(output_filepath);

    // Stop measuring time
    std::clock_t end = std::clock();

    // Calculate the elapsed time in seconds
    double elapsed_time = static_cast<double>(end - start) / CLOCKS_PER_SEC;

    // Print the elapsed time
    if (debug) {
        std::cout << "Simulation ends" << std::endl;
        std::cout << "Elapsed time: " << elapsed_time << " seconds." << std::endl;
    }

    return 0;
}
