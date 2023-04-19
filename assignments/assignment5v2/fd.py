import matplotlib.pyplot as plt
import numpy as np


def main():
    input_file = open("output", "r")
    content = list(filter(lambda x: x.strip() != "", input_file.readlines()))

    values = []
    for i in range(len(content)):
        # clean it
        prefix_to_cut = "sketch.js:284"
        line = content[i]
        if prefix_to_cut in line and line[0] == prefix_to_cut[0]:
            content[i] = line.removeprefix(prefix_to_cut)

        # parse the tree parts
        items = content[i].split("|")
        items = list(map(lambda x: x.strip(), items))
        step = int(items[0])
        num_ppl = int(items[1])
        times = list(map(lambda x: int(x), items[2].split()))
        values.append((step, num_ppl, times))

    values.sort(key=lambda x: x[0])

    speed_density_pairs = []
    idx = -1
    for (step, num_ppl, times) in values:
        idx += 1
        #print((step, num_ppl, times))

        # ignore initial values which may be weird due to model still converging
        # also limit iterations to 10k
        if step < 500 or step > 10000:
            continue

        # we only care about steps when some particle went out
        if not times:
            continue

        # there can be more times
        for t in times:
            # get all densities for last t steps
            num_ppl_sum = 0
            for (_, prev_num_ppl, _) in values[idx - t: idx + 1]:
                num_ppl_sum += prev_num_ppl
            num_ppl_avg = num_ppl_sum / t

            if num_ppl_sum == 0:
                print(step)

            # compute speed and density and save
            speed = 2 / t
            density = num_ppl_avg / 2
            speed_density_pairs.append((speed, density))

    # TODO: plot results as scatter plot
    speeds = np.array([s for (s, _) in speed_density_pairs])
    densities = np.array([d for (_, d) in speed_density_pairs])
    plt.scatter(densities, speeds)
    plt.show()


if __name__ == "__main__":
    main()
