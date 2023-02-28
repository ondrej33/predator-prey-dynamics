import os
import numpy
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt

from sklearn import metrics


def auc(labeled_data, index, image_pth='roc_curve.png', max_r=9):
    # sort the data with respect to negsel scores
    labeled_data.sort(key=lambda x: x[0])
    #print(labeled_data)

    # get a list of unique scores
    unique_vals = sorted(list(set([x[0] for x in labeled_data])))
    #print(unique_vals)

    # compute the FP and TP rates
    len_pos = len([x for x in labeled_data if x[1] == 0])
    len_neg = len([x for x in labeled_data if x[1] == 1])
    fp_rate = [0.0]
    tp_rate = [0.0]
    for i in unique_vals:
        fp_rate.append(len([x for x in labeled_data if x[1] == 0 and x[0] >= i]) / len_pos)
        tp_rate.append(len([x for x in labeled_data if x[1] == 1 and x[0] >= i]) / len_neg)

    fp_rate = numpy.array(sorted(fp_rate))
    tp_rate = numpy.array(sorted(tp_rate))
    fp_rate = numpy.append(fp_rate, 1)
    tp_rate = numpy.append(tp_rate, 1)
    #print(fp_rate)
    #print(tp_rate)

    # computation both directly and by using sklearn
    auc_v_1 = sum(numpy.diff(fp_rate) * (tp_rate[1:] + tp_rate[:-1])) / 2
    auc_v = metrics.auc(fp_rate, tp_rate)
    assert abs(auc_v_1 - auc_v) < 0.001

    plt.title('Receiver Operating Characteristic')
    plt.plot(fp_rate, tp_rate, label=f'r={index}, AUC = {auc_v:.2f}', color=list(mcolors.TABLEAU_COLORS)[index % 10])
    plt.legend(loc='lower right')
    plt.plot([0, 1], [0, 1], 'r--')
    plt.xlim([0, 1])
    plt.ylim([0, 1])
    plt.ylabel('True Positive Rate')
    plt.xlabel('False Positive Rate')

    if index == max_r:
        plt.savefig(image_pth)
    return auc_v


if __name__ == "__main__":
    auc_list = []
    for r_val in range(1, 10):

        # generate scores for merged set
        bash_command = f"java -jar negsel2.jar -l -c -n 10 -r {r_val} -self english.train < merged.test"
        data = os.popen(bash_command).read()
        data_floats = [float(x) for x in data.split()]

        # load the labels for merged set
        labels_file = open("merged.labels", "r")
        data_labels = [int(x) for x in labels_file.read().split()]
        assert len(data_floats) == len(data_labels)

        auc_value = auc(list(zip(data_floats, data_labels)), r_val)
        auc_list.append(auc_value)
        print(f"{r_val}:  {auc_value}")

    print(auc_list)
    print(f"mean: {sum(auc_list) / len(auc_list)}, max: {max(auc_list)}, min: {min(auc_list)}")
