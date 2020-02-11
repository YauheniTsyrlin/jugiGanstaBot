import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
from datetime import datetime
import config

def getPlot(cursor, username: str):
    #Make a query to the specific DB and Collection
    # Expand the cursor and construct the DataFrame
    df =  pd.DataFrame(list(cursor))
    df['date'] = [datetime.fromtimestamp(x).strftime("%d/%m") for x in df.date]

    # # Delete the _id
    if True:
        del df['_id']
        del df['login']
        del df['damage']
        del df['armor']
        del df['dzen']
        del df['stamina']

    columns_name = {
            'force'     :'Сила',
            'accuracy'  :'Меткость',
            'health'    :'Здоровье',
            'agility'   :'Ловкость',
            'charisma'  :'Харизма'
            }

    columns_color = {
            'force'     :'gold',
            'accuracy'  :'tab:green',
            'health'    :'tab:red',
            'agility'   :'darkgrey',
            'charisma'  :'mediumblue'
            }

    # Define the upper limit, lower limit, interval of Y axis and colors
    y_interval = 50
    # Draw Plot and Annotate
    fig, ax = plt.subplots(1,1,figsize=(12, 7), dpi= 80)  

    y_LL = []
    columns = df.columns[1:]  
    for i, column in enumerate(columns):    
        plt.plot(df.date.values, df[column].values, lw=1.5, color=columns_color[column]) 
        # plt.text(df.shape[0]+1, df[column].values[-1], f'{column} {df[column].max()}')
        y_LL.append(int(df[column].max().max()*1.1))
        ax.plot(df.date.values, df[column].values, label = f'{df[column].max()} {columns_name[column]}', color=columns_color[column])

    # Draw Tick lines  
    for y in range(min(y_LL), max(y_LL), y_interval):    
        plt.hlines(y, xmin=0, xmax=10, colors='black', alpha=0.3, linestyles="--", lw=0.5)

    # Decorations    
    plt.tick_params(axis="both", which="both", bottom=False, top=False, labelbottom=True, left=False, right=False, labelleft=True)        

    # Lighten borders
    plt.gca().spines["top"].set_alpha(.3)
    plt.gca().spines["bottom"].set_alpha(.3)
    plt.gca().spines["right"].set_alpha(.3)
    plt.gca().spines["left"].set_alpha(.3)
    plt.title('Прогресс Пип-боев', fontsize=22)
    plt.yticks(range( int(( min(y_LL)//y_interval - 1)* y_interval), max(y_LL) + 2*y_interval, y_interval), [str(y) for y in range(int(( min(y_LL)//y_interval - 1)* y_interval), max(y_LL) + 2*y_interval , y_interval)], fontsize=12)    
    plt.xticks(range(0, 14), df.date.values, horizontalalignment='left', fontsize=12)    
    plt.ylim(min(y_LL)-2*y_interval, max(y_LL))    
    plt.xlim(0, df.shape[0]+1) 
    ax.legend()
    fig.savefig(config.PATH_IMAGE + f'plot_{username}.png', dpi=fig.dpi)