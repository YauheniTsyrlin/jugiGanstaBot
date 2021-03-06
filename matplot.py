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

    # Draw Plot and Annotate
    fig, ax = plt.subplots(1,1,figsize=(10, 10), dpi= 80)  

    y_MAX = []
    y_MIN = []
    columns = df.columns[1:]  
    for i, column in enumerate(columns):    
        plt.plot(df.date.values, df[column].values, lw=1.5, color=columns_color[column]) 
        # plt.text(df.shape[0]+1, df[column].values[-1], f'{column} {df[column].max()}')
        plt.scatter(df.date.values, df[column].values, edgecolors=columns_color[column], c=columns_color[column], s=40)
        y_MAX.append(int(df[column].max().max()))
        y_MIN.append(int(df[column].min().min()))
        ax.plot(df.date.values, df[column].values, label = f'{df[column].max()} {columns_name[column]}', color=columns_color[column])

    y_interval = 100


    # Draw Tick lines  
    # for y in range(0, max(y_LL), y_interval):    
    #     plt.hlines(y, xmin=0, xmax=10, colors='black', alpha=0.3, linestyles="--", lw=0.5)


    # Decorations    
    plt.tick_params(axis="both", which="both", bottom=False, top=False, labelbottom=True, left=False, right=False, labelleft=True)        

    # Lighten borders
    plt.gca().spines["top"].set_alpha(.3)
    plt.gca().spines["bottom"].set_alpha(.3)
    plt.gca().spines["right"].set_alpha(.3)
    plt.gca().spines["left"].set_alpha(.3)
    plt.title(f'Прогресс Пип-боев {username}', fontsize=22)

    plt.yticks(range( 0, max(y_MAX) + y_interval, y_interval), [str(y) for y in range( 0, max(y_MAX) + y_interval  , y_interval)], fontsize=12)    
    plt.xticks(range(0, 10), df.date.values, horizontalalignment='left', fontsize=12)    
    plt.ylim( int( min(y_MIN) - y_interval ), int( max(y_MAX) + y_interval) )    
    plt.xlim(0, 10) 
    ax.legend()

    # Shrink current axis's height by 10% on the bottom
    box = ax.get_position()
    ax.set_position([box.x0, box.y0 + box.height * 0.1,
                    box.width, box.height * 0.9])

    # Put a legend below current axis
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05),
            fancybox=True, shadow=True, ncol=5, prop={'size': 12})
    ax.grid()
    fig.savefig(config.PATH_IMAGE + f'plot_{username}.png', dpi=fig.dpi)


def getPlotСourse(cursor, username: str):
    #Make a query to the specific DB and Collection
    # Expand the cursor and construct the DataFrame
    df =  pd.DataFrame(list(cursor))
    df['date'] = [datetime.fromtimestamp(x).strftime("%d/%m") for x in df.date]
    inventory_name = df['inventory_name'][0]

    # # Delete the _id ...
    if True:
        del df['_id']
        del df['seller']
        del df['buyer']
        del df['inventory_id']
        del df['inventory']
        del df['inventory_name']
    print(df)
    columns_name = {
            'cost'     :'Цена'
            }

    columns_color = {
            'cost'     :'tab:green'
            }

    # Define the upper limit, lower limit, interval of Y axis and colors

    # Draw Plot and Annotate
    fig, ax = plt.subplots(1, 1, figsize=(10, 10), dpi= 80)  

    y_MAX = []
    y_MIN = []
    columns = df.columns[1:]  
    for i, column in enumerate(columns):    
        plt.plot(df.date.values, df[column].values, lw=1.5, color=columns_color[column]) 
        plt.scatter(df.date.values, df[column].values, edgecolors=columns_color[column], c=columns_color[column], s=40)
        y_MAX.append(int(df[column].max().max()))
        y_MIN.append(int(df[column].min().min()))
        ax.plot(df.date.values, df[column].values, label = f'{df[column].max()} {columns_name[column]}', color=columns_color[column])

    y_interval = 50
    
    # [datetime.fromtimestamp(x).strftime("%d/%m") for x in df.date]
    
    # Draw Tick lines  
    # for y in range(0, max(y_LL), y_interval):    
    #     plt.hlines(y, xmin=0, xmax=10, colors='black', alpha=0.3, linestyles="--", lw=0.5)


    # Decorations    
    plt.tick_params(axis="both", which="both", bottom=False, top=False, labelbottom=True, left=False, right=False, labelleft=True)        

    # Lighten borders
    plt.gca().spines["top"].set_alpha(.3)
    plt.gca().spines["bottom"].set_alpha(.3)
    plt.gca().spines["right"].set_alpha(.3)
    plt.gca().spines["left"].set_alpha(.3)
    plt.title(f'{inventory_name}', fontsize=22)

    N = 14
    plt.yticks(range( 0, max(y_MAX) + y_interval, y_interval), [str(y) for y in range( 0, max(y_MAX) + y_interval  , y_interval)], fontsize=12)    
    plt.xticks(range(0, N), df.date.values, horizontalalignment='left', fontsize=12)    
    plt.ylim( int( min(y_MIN) - y_interval ), int( max(y_MAX) + y_interval) )    
    plt.xlim(0, N) 
    ax.legend()

    # Shrink current axis's height by 10% on the bottom
    box = ax.get_position()
    ax.set_position([box.x0, box.y0 + box.height * 0.1,
                    box.width, box.height * 0.9])

    # ax.set_xticklabels(df.date.values,
    #                fontsize = 15,    #  Размер шрифта
    #                color = 'b',    #  Цвет текста
    #                rotation = 90,    #  Поворот текста
    #                verticalalignment =  'center')    #  Вертикальное выравнивание



    # Put a legend below current axis
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05),
            fancybox=True, shadow=True, ncol=5, prop={'size': 12})
    ax.grid()
    fig.savefig(config.PATH_IMAGE + f'graf_{username}.png', dpi=fig.dpi)