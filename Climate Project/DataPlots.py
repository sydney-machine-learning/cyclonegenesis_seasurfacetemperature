from cmath import sqrt
import csv
import matplotlib.pyplot as plt
import numpy as np


def plot(filename):
    with open(filename) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        col_names = {}
        wind_intensity_sum = {}
        wind_intensity_cnt = {}
        for row in csv_reader:
            if line_count == 0:
                for i in range(0, len(row)):
                    col_names[row[i]] = i
                line_count = 1
            else:
                if int(row[col_names["No. of Cycl"]]) in wind_intensity_cnt:
                    wind_intensity_cnt[int(row[col_names["No. of Cycl"]])] += 1
                    wind_intensity_sum[int(
                        row[col_names["No. of Cycl"]])] += int(row[col_names["Speed(knots)"]])
                else:
                    wind_intensity_cnt[int(row[col_names["No. of Cycl"]])] = 1
                    wind_intensity_sum[int(row[col_names["No. of Cycl"]])] = int(
                        row[col_names["Speed(knots)"]])
        wind_intensity_average = {}
        for cyclone_id in wind_intensity_cnt:
            wind_intensity_average[cyclone_id] = wind_intensity_sum[cyclone_id] / \
                wind_intensity_cnt[cyclone_id]
        wind_intensity_variance = {}
        wind_intensity_std = {}
        cnt = 0
    with open(filename) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            if(cnt == 0):
                cnt += 1
                continue
            if int(row[col_names["No. of Cycl"]]) in wind_intensity_variance:
                wind_intensity_variance[int(row[col_names["No. of Cycl"]])] += (int(
                    row[col_names["Speed(knots)"]])-wind_intensity_average[int(row[col_names["No. of Cycl"]])])**2
            else:
                wind_intensity_variance[int(row[col_names["No. of Cycl"]])] = (int(
                    row[col_names["Speed(knots)"]])-wind_intensity_average[int(row[col_names["No. of Cycl"]])])**2
        for cyclone_id in wind_intensity_cnt:
            wind_intensity_variance[cyclone_id] /= wind_intensity_cnt[cyclone_id]
            wind_intensity_std[cyclone_id] = sqrt(
                wind_intensity_variance[cyclone_id])
        cyclone_data = []
        for cyclone_id in wind_intensity_average:
            cyclone_data.append(
                [cyclone_id, wind_intensity_average[cyclone_id], wind_intensity_std[cyclone_id]])
        cyclone_data.sort()
        cyclone_ids = []
        wind_intensity_averages = []
        wind_intensity_stds = []
        for item in cyclone_data:
            cyclone_ids.append(item[0])
            wind_intensity_averages.append(item[1])
            wind_intensity_stds.append(item[2])
        xpoints = np.array(cyclone_ids)
        fig, ax = plt.subplots()
        ax.bar(xpoints, wind_intensity_averages, yerr=wind_intensity_stds,
               align='center', alpha=0.5, ecolor='black', capsize=10)
        ax.set_ylabel("Mean wind intensity")
        ax.set_xticks(xpoints)
        ax.set_title("Wind Intensity of Cyclones")
        ax.yaxis.grid(True)
        plt.xlabel("Cyclone ID")

        plt.tight_layout()
        plt.show()


def plot_mean_SD(filename):
    with open(filename) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        col_names = {}
        cyclone_ids = {}
        for row in csv_reader:
            print(row)
            if line_count == 0:
                for i in range(0, len(row)):
                    col_names[row[i]] = i
                line_count = 1
            else:
                if int(row[col_names["No. of Cycl"]]) not in cyclone_ids:
                    cyclone_ids[int(row[col_names["No. of Cycl"]])] = [float(row[col_names["Week_1_Mean"]]), float(row[col_names["Week_2_Mean"]]), float(row[col_names["Week_3_Mean"]]), float(
                        row[col_names["Week_4_Mean"]]), float(row[col_names["Week_1_SD"]]), float(row[col_names["Week_2_SD"]]), float(row[col_names["Week_3_SD"]]), float(row[col_names["Week_4_SD"]])]
    l = []
    for key in cyclone_ids:
        l.append(key)
    xpoints = np.array(l)
    data_mean = [[], [], [], []]
    data_std = [[], [], [], []]
    for item in cyclone_ids:
        for i in range(4):
            data_mean[i].append(cyclone_ids[item][i])
        for i in range(4, 8):
            data_std[i-4].append(cyclone_ids[item][i])
    fig, ax = plt.subplots()
    ax.bar(xpoints, data_mean[0], yerr=data_std[0],
           align='center', alpha=0.5, ecolor='black', capsize=10)
    ax.set_ylabel("Mean Sea Surface Temperature")
    ax.set_xticks(xpoints)
    ax.set_title("Week 4 Sea Surface Temperature")
    ax.yaxis.grid(True)
    # ax[0, 1].bar(xpoints, data_mean[1], yerr=data_std[1], align='center', alpha=0.5, ecolor='black', capsize=10)
    # ax[0, 1].set_ylabel("Mean Sea Surface Temperature")
    # ax[0, 1].set_xticks(xpoints)
    # ax[0, 1].set_yticks(list(range(280, 340, 5)))
    # ax[0, 1].set_title("Week 2 Sea Surface Temperature")
    # ax[0, 1].yaxis.grid(True)
    # ax[1, 0].bar(xpoints, data_mean[2], yerr=data_std[2], align='center', alpha=0.5, ecolor='black', capsize=10)
    # ax[1, 0].set_ylabel("Mean Sea Surface Temperature")
    # ax[1, 0].set_xticks(xpoints)
    # ax[1, 0].set_yticks(list(range(280, 340, 5)))
    # ax[1, 0].set_title("Week 3 Sea Surface Temperature")
    # ax[1, 0].yaxis.grid(True)
    # ax[1, 1].bar(xpoints, data_mean[3], yerr=data_std[3], align='center', alpha=0.5, ecolor='black', capsize=10)
    # ax[1, 1].set_ylabel("Mean Sea Surface Temperature")
    # ax[1, 1].set_xticks(xpoints)
    # ax[1, 1].set_yticks(list(range(280, 340, 5)))
    # ax[1, 1].set_title("Week 4 Sea Surface Temperature")
    # ax[1, 1].yaxis.grid(True)

    plt.ylim(275, 305)
    plt.tight_layout()
    plt.show()


path = input("Enter csv path for SI_MEAN_SD: ")
plot_mean_SD(path)
