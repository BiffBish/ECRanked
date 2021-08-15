import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import (MultipleLocator, AutoMinorLocator)
from core.constants import GAMEMODENAMES
from datetime import *
from dateutil import tz

async def TimeOfDayHist(bot):
    return



    pubGames = bot.database.get_pub_games()
    timesOfDay = []
    from_zone = tz.tzutc()
    to_zone = tz.tzlocal()  
    nowhour = datetime.now().hour
    nowmin = datetime.now().minute
    
    nowhourdec = nowhour + (nowmin/60)
    
    for game in pubGames:
        t1 = datetime.strptime(game["time"], '%Y-%m-%d %H:%M:%S')
        t1 = t1.replace(tzinfo=from_zone)
        t2 = t1.astimezone(to_zone)
        t2hourdec = t2.hour + (t2.minute) / 60
        t2hourdec -= (nowhourdec-12)
        t2hourdec %= 24
        timesOfDay.append(t2hourdec)


    

    print(timesOfDay)
    n_bins = 24

    print(datetime.now().hour)
    fig, ax = plt.subplots(facecolor=(.1,.1,.1,0))
    ax.set_facecolor('#000')
    fig.patch.set_facecolor('black')
    #ax.set_ylim(800, 1200)
    #ax.set_title(GAMEMODENAMES[Gamemode],color= "white")
    
    ax.tick_params(axis='y', colors='white')
    ax.tick_params(axis='x', colors='white')

    ax.spines['left'].set_color('white')        # setting up Y-axis tick color to red
    ax.spines['top'].set_color('white')
    ax.spines['right'].set_color('white')        # setting up Y-axis tick color to red
    ax.spines['bottom'].set_color('white')
    #ax.xaxis.set_major_locator(MultipleLocator(5))
    #ax.xaxis.set_major_formatter('{x:.0f}')
    #ax.tick_params(which='minor', length=4, color='w')
    #ax.tick_params(which='major', length=7, color='w')
    # We can set the number of bins with the `bins` kwarg
    
    ax.set_xlim([0,24])
    print(list(range(25)))
    ax.hist(timesOfDay, bins=list(range(0,24,1)))
    ax.axvline(12,color="red")
    print(ax.get_ylim())
    #ax.text(nowhourdec,ax.get_ylim()[1],'Now',
    #    color="red",
    #    horizontalalignment='left',
    #    verticalalignment='top',
     #   )

    plt.xticks(ticks=list(range(25)), labels=["-12h","","","-9h","","","-6h","","","-3h","","","Now","","","+3h","","","+6h","","","+9h","","","12am"])
    ax.xaxis.set_minor_locator(MultipleLocator(1))

    plt.title("Time of Day of Pubs",color="white")
    
    #ax.hist(timesOfDay, bins=n_bins,facecolor='g')
    #plt.setp(ax.get_xticklabels(), rotation=0, ha="center",color = "white")
    plt.savefig('stats.png')