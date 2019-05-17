import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import math
import json
from pathlib import Path

def findClosest(mza, intensitya,mz):
    ix = min(range(len(mza)),key=lambda i: abs(mza[i]-mz))
    return mza[ix],intensitya[ix]

def main():
    result_file = Path("./results.pkl")
    if not result_file.exists():
        json_file = 'boxcar.json'
        prev_data = json.load(open(json_file, 'rb'))
        mzdiff,intdiff = [],[]
        for (mz_arrays, intensity_arrays) in prev_data:
            for index, (mza, intensitya) in enumerate(zip(mz_arrays, intensity_arrays)):
                if index == 0:
                    legend = 'MS1'
                    ms1 = (mza, intensitya)
                else:
                    legend = 'Boxcar ' + str(index)
                if index>=1:
                    firstmz,lastmz = .0,.0
                    for mz, intensity in zip(mza, intensitya):
                        ms1mz,ms1int = findClosest(ms1[0],ms1[1],mz)
#                        if abs(ms1mz-mz) < 0.0005:
                        if abs(ms1mz-mz) < 0.0002:
                            print(mz, intensity, ms1mz, ms1int)
                            if mz-lastmz>400:
                                firstmz = mz
                            mzdiff += [mz-firstmz]
                            intdiff += [math.log2(intensity/ms1int)]
                            lastmz = mz
        result_df = pd.DataFrame({'m/z':mzdiff,'Intensity fold change':intdiff})
        result_df.to_pickle(result_file)
    else:
        result_df = pd.read_pickle(result_file)
    sns.set_style("whitegrid")
    g = sns.JointGrid(x="m/z", y="Intensity fold change", data=result_df,height=7, ratio=6)
    g = g.plot_joint(sns.kdeplot, cmap="Reds_d")
    g = g.plot_marginals(sns.kdeplot, color="r", shade=True)
    plt.savefig('boxcar_biases.png')
    plt.show()


if __name__ == '__main__':
    main()
