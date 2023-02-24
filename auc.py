import os
import numpy


def auc(labeled_data):
    labeled_data.sort(key=lambda x: x[0])
    #print(labeled_data)

    unique_vals = sorted(list(set([x[0] for x in labeled_data])))
    #print(unique_vals)

    len_pos = len([x for x in labeled_data if x[1] == 1])
    len_neg = len([x for x in labeled_data if x[1] == 0])

    fp_rate = [0.0]
    tp_rate = [0.0]
    for i in unique_vals:
        fp_rate.append(len([x for x in labeled_data if x[1] == 1 and x[0] >= i]) / len_pos)
        tp_rate.append(len([x for x in labeled_data if x[1] == 0 and x[0] >= i]) / len_neg)

    fp_rate = numpy.array(sorted(fp_rate))
    tp_rate = numpy.array(sorted(tp_rate))
    #print(fp_rate)
    #print(tp_rate)

    return 1 - sum(numpy.diff(fp_rate) * (tp_rate[1:] + tp_rate[:-1])) / 2


if __name__ == "__main__":
    for r_val in range(1, 10):

        # generate scores for merged set
        bash_command = f"java -jar negsel2.jar -l -c -n 10 -r {r_val} -self english.train < merged.test"
        data = os.popen(bash_command).read()
        #| paste - merged.labels | R -f ./auc.r
        data_floats = [float(x) for x in data.split()]

        # load the labels for merged set
        labels_file = open("merged.labels", "r")
        data_labels = [int(x) for x in labels_file.read().split()]

        auc_value = auc(list(zip(data_floats, data_labels)))
        print(f"{r_val}:  {auc_value}")
