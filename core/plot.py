import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
from matplotlib.ticker import (MultipleLocator, AutoMinorLocator)
from core.constants import GAMEMODENAMES

def statPlot(stats,Gamemode = 0):
    elos = stats["eloHistory"][Gamemode]
    print(elos)
    #x = [datetime.fromisoformat(d) for d in elos[0]]
    
    
    fig, ax = plt.subplots(facecolor=(.1,.1,.1,0))
    ax.set_facecolor('#000')
    fig.patch.set_facecolor('black')
    ax.set_ylim(800, 1200)
    ax.set_title(GAMEMODENAMES[Gamemode],color= "white")
    ax.tick_params(axis='y', colors='white')
    ax.spines['left'].set_color('white')        # setting up Y-axis tick color to red
    ax.spines['top'].set_color('white')
    ax.spines['right'].set_color('white')        # setting up Y-axis tick color to red
    ax.spines['bottom'].set_color('white')
    ax.xaxis.set_major_locator(MultipleLocator(5))
    ax.xaxis.set_major_formatter('{x:.0f}')
    ax.xaxis.set_minor_locator(MultipleLocator(1))
    ax.tick_params(which='minor', length=4, color='w')
    ax.tick_params(which='major', length=7, color='w')
    
    


    x = np.arange(len(elos)+1)
    elos = [result[2] for result in elos]
    elos.append(elos[-1])
    print(elos)

    #ax.plot(x, elos,color='red')
    ax.step(x, elos, where='post',color='white')

    ax.axhline(stats["maxElo"][Gamemode],color=(0,1,0,.5),linestyle = ":")
    ax.axhline(stats["minElo"][Gamemode],color=(1,0,0,.5),linestyle = ":")

    ax.axvspan(stats["eloWinStreakStart"][Gamemode] ,stats["eloWinStreakStart"][Gamemode] + stats["eloWinStreakLength"][Gamemode] , facecolor="#2CA02Ccc")
    ax.axvspan(stats["eloLossStreakStart"][Gamemode] ,stats["eloLossStreakStart"][Gamemode] + stats["eloLossStreakLength"][Gamemode] ,facecolor="#d12b15cc")

    # for i in stats["winGames"][Gamemode]:
    #     ax.axvspan(i,i+1 ,facecolor="#2CA02C55")

    # for i in stats["lossGames"][Gamemode]:
    #     ax.axvspan(i,i+1 ,facecolor="#d12b1555")

    # ax.step(x, elos[2], where='post',color='green', label='Linked Random Loadout')
    # ax.axhline(stats["maxElos"][1],color=(0,1,0,.3),linestyle = ":")
    # ax.axhline(stats["minElos"][1],color=(0,1,0,.3),linestyle = ":")
    #ax.step(x, elos[3], where='post',color='yellow', label='Standard 1v1')
    #ax.step(x, elos[4], where='post',color='orange', label='Standard 2v2')
    

    #ax.plot(x, y, 'o--', color='grey', alpha=0.3)

    ax.grid(axis='x', color='0.05')
    #ax.legend(title='Elo History')
    plt.setp(ax.get_xticklabels(), rotation=0, ha="center",color = "white")
    plt.savefig('stats.png')
    #plt.show()


def globalStatPlot(stats,Gamemode = 0):
    
    
    fig, ax = plt.subplots(facecolor=(.1,.1,.1,0))
    ax.set_facecolor('#000')
    fig.patch.set_facecolor('black')
    ax.set_ylim(800, 1200)
    ax.set_title(GAMEMODENAMES[Gamemode],color= "white")
    ax.tick_params(axis='y', colors='white')
    ax.spines['left'].set_color('white')        # setting up Y-axis tick color to red
    ax.spines['top'].set_color('white')
    ax.spines['right'].set_color('white')        # setting up Y-axis tick color to red
    ax.spines['bottom'].set_color('white')
    ax.xaxis.set_major_locator(MultipleLocator(5))
    ax.xaxis.set_major_formatter('{x:.0f}')
    ax.xaxis.set_minor_locator(MultipleLocator(1))
    ax.tick_params(which='minor', length=4, color='w')
    ax.tick_params(which='major', length=7, color='w')
    


    for key, value in stats.items():

        history = value["eloHistory"][Gamemode]
        times = [datetime.fromisoformat(result[0]) for result in history]

        #times = [result[0] for result in history]
        elos = [result[2] for result in history]


        #ax.plot(x, elos,color='red')
        ax.step(times, elos, where='post',color="#ffffff33")
    
    ax.xaxis.set_major_locator(mdates.DayLocator(bymonthday=None, interval=7))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    plt.setp(ax.get_xticklabels(), rotation=30, ha="right")
    #ax.plot(x, y, 'o--', color='grey', alpha=0.3)

    ax.grid(axis='x', color='0.05')
    #ax.legend(title='Elo History')
    plt.setp(ax.get_xticklabels(), rotation=0, ha="center",color = "white")
    plt.savefig('stats.png')
    #plt.show()
