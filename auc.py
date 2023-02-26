import os
import numpy
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt


def auc(labeled_data, index, image_pth='roc_curve.png', max_r=9):
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

    auc_v = 1 - sum(numpy.diff(fp_rate) * (tp_rate[1:] + tp_rate[:-1])) / 2

    plt.title('Receiver Operating Characteristic')
    plt.plot(tp_rate, fp_rate, label=f'r={index}, AUC = {auc_v:.2f}', color=list(mcolors.TABLEAU_COLORS)[index])
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
    for r_val in range(1, 10):

        # generate scores for merged set
        bash_command = f"java -jar negsel2.jar -l -c -n 10 -r {r_val} -self english.train < merged.test"
        data = os.popen(bash_command).read()
        #| paste - merged.labels | R -f ./auc.r
        data_floats = [float(x) for x in data.split()]

        # load the labels for merged set
        labels_file = open("merged.labels", "r")
        data_labels = [int(x) for x in labels_file.read().split()]

        auc_value = auc(list(zip(data_floats, data_labels)), r_val)
        print(f"{r_val}:  {auc_value}")
