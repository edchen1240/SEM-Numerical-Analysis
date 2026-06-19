"""
[F14_Stock.py]
Purpose: store function for ILH project.
Author: Meng-Chi Ed Chen
Date: 2023-06-06
Reference:
    1.
    2.

Status: Complete.
"""
import os, sys
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
import tensorflow

from datetime import date, datetime, timedelta
import pandas as pd
import yfinance as yf
import numpy as np
import openpyxl

import torch
import torch.nn as nn
from torch.utils.data import Dataset

# SPP-1_
def basename_process(stock_ticker, start_date, end_date):
    print('\n[basename_process]')
    if stock_ticker == '2330.TW':
        stock_file_lable = 'TSMC'
    elif stock_ticker == 'TSM':
        stock_file_lable = 'TSM'
    basename_excel = stock_file_lable + '_' + start_date + '~' + end_date + '.xlsx'
    print('-- basename_excel will be', basename_excel)
    return basename_excel

# SPP-1_
def download_stockprice_rawdata(start_date, end_date, stock_ticker):
    print('\n[save_stockprice_rawdata]')
    #[] Date format process.
    if not isinstance(start_date, date):
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    if not isinstance(end_date, date):
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    print('\n[Input date check] start_date:', start_date, type(start_date), '; end_date:  ', end_date, type(end_date))
    #[] Get fresh stock price from Yahoo.
    df_stock_data = yf.download(stock_ticker, start=start_date, end=end_date, interval="1d")
    #[] Convert the index to date only if it's a datetime
    if isinstance(df_stock_data.index, pd.DatetimeIndex):
        df_stock_data.index = df_stock_data.index.date
        df_stock_data.index.name = "Date"
    #[] Show dataframe information.
    print('\n[Dataframe info]')
    print(df_stock_data.info(), '\n')
    return df_stock_data

# SPP-1_
def line_graph(df_stock_data, stock_ticker, path_image_save):
    print('\n[quick_graph]')
    import matplotlib.pyplot as plt
    fig, ax1 = plt.subplots(figsize=(8, 6))
    ax2 = ax1.twinx()  # Generate a second axes that shares the same x-axis
    ax1.plot(df_stock_data.index, df_stock_data['Close'], color='C0')
    ax2.bar(df_stock_data.index, df_stock_data['Volume'], color='m')

    ax1.set_xlabel('Date')
    ax1.set_ylabel('Close Price', color='C0')
    ax2.set_ylabel('Volume', color='m')
    ax1.set_ylim([min(df_stock_data['Close']*0.8), max(df_stock_data['Close'])*1.1])
    ax2.set_ylim([0, max(df_stock_data['Volume'])*4])

    new_start_date = df_stock_data.index.min().strftime("%Y-%m-%d")
    new_end_date = df_stock_data.index.max().strftime("%Y-%m-%d")
    chart_title = stock_ticker + ' Price Line Graph\n(from ' + new_start_date + ' to ' \
                    + new_end_date + ', ' + str(df_stock_data.shape) + ')'

    plt.setp(ax1.get_xticklabels(), rotation=20, horizontalalignment='right')
    plt.title(chart_title)
    path_image_save = path_image_save.replace('.png', '_1-line_.png')
    plt.savefig(path_image_save)
    #plt.show()





# SPP-1_, SPP-2_
def save_stockprice_to_excel(df_stock_data, dir_excel, basename_excel, sheet_name_or_index):
    print('\n[save_stockprice_to_excel]')
    # Convert sheet index to string name if an integer is provided
    if isinstance(sheet_name_or_index, int):
        sheet_name = f'Sheet{sheet_name_or_index}'
    else:
        sheet_name = str(sheet_name_or_index)  # Ensure sheet_name is always a string
    # Ensure the directory exists
    if not os.path.exists(dir_excel):
        os.makedirs(dir_excel)
    path_excel = os.path.join(dir_excel, basename_excel)
    # Check if the file exists
    if os.path.isfile(path_excel):
        book = openpyxl.load_workbook(path_excel)
        # If the file and sheet both exist, remove existing sheet
        if sheet_name in book.sheetnames:
            del book[sheet_name]
        with pd.ExcelWriter(path_excel, engine='openpyxl', mode='a', if_sheet_exists='new') as writer: #Close the file
            df_stock_data.to_excel(writer, sheet_name=sheet_name, index=True)
    else:  # If file doesn't exist, create a new one
        with pd.ExcelWriter(path_excel, engine='openpyxl', mode='w') as writer:
            df_stock_data.to_excel(writer, sheet_name=sheet_name, index=True)
    # Adjust column width
    adjust_column_width(path_excel, sheet_name, 'A', 12)
    print(f'Data saved to {path_excel} in sheet {sheet_name}', end='\n\n')
        

def adjust_column_width(path_excel, sheet_name, column_name, desired_width):
    print('\n[adjust_column_width]')
    # Load the workbook and the specific sheet
    workbook = openpyxl.load_workbook(path_excel)
    if sheet_name not in workbook.sheetnames:
        print(f"--Sheet '{sheet_name}' does not exist in the workbook.")
        return
    worksheet = workbook[sheet_name]
    worksheet.column_dimensions[column_name].width = desired_width
    workbook.save(path_excel)
    print(f"--Column '{column_name}' in sheet '{sheet_name}' has been adjusted to width {desired_width}.", end='\n\n')
        
# SPP-1_, SPP-2_
def read_stockprice_from_excel(path_excel, sheet_name):
    print('\n[read_stockprice_from_excel]')
    df_stock_data = pd.read_excel(path_excel, sheet_name=sheet_name, index_col=0)
    #[] Convert the index to date only if it's a datetime
    if isinstance(df_stock_data.index, pd.DatetimeIndex):
        df_stock_data.index = df_stock_data.index.date
        df_stock_data.index.name = "Date"
    #[] Check start and end date
    start_date = df_stock_data.index.min()
    end_date = df_stock_data.index.max()
    print('--[Path]', path_excel)
    print('--[Index]', str(start_date), 'to', str(end_date))
    print('--[Shape]', df_stock_data.shape, end='\n\n')
    return df_stock_data


# SPP-1_
def candlestick_graph(df_stock_data, stock_ticker, path_image_save):
    print('\n[candlestick_graph]')
    import matplotlib.pyplot as plt
    from plotly.subplots import make_subplots
    import plotly.graph_objects as go

    # Open secondary axis.
    fig1 = make_subplots(specs=[[{"secondary_y": True}]])
    fig1.update_layout(width=800, height=600)  # Update this line
    # Plot OHLC on main axis.
    fig1.add_trace(go.Candlestick(x=df_stock_data.index,
                                open=df_stock_data['Open'],
                                high=df_stock_data['High'],
                                low=df_stock_data['Low'],
                                close=df_stock_data['Close']
                                ))
    close_max_value = df_stock_data['Close'].max()
    close_min_value = df_stock_data['Close'].min()
    fig1.update_yaxes(range=[close_min_value*0.9, close_max_value*1.05], secondary_y=False)

    # Moving average.
    fig1.add_trace(go.Scatter(x=df_stock_data.index,
                            y=df_stock_data['Close'].rolling(window=20).mean(),
                            marker_color='blue',
                            name='20 Day MA'))

    # Color of volume bar.
    df_stock_data['Volume-diff'] = df_stock_data['Volume'] - df_stock_data['Volume'].shift(1)
    df_stock_data['Volume-diff'] = df_stock_data['Volume-diff'].fillna(0)
    df_stock_data.loc[df_stock_data['Volume-diff'] >= 0, 'Volume-color'] = 'green'
    df_stock_data.loc[df_stock_data['Volume-diff'] < 0, 'Volume-color'] = 'red'


    # Volume chart.
    volume_max_value = df_stock_data['Volume'].max()
    fig1.add_trace(go.Bar(x=df_stock_data.index,
                        y=df_stock_data['Volume'],
                        name='Volume',
                        marker={'color': df_stock_data['Volume-color']}), secondary_y=True)
    fig1.update_yaxes(range=[0, volume_max_value*10], secondary_y=True)
    fig1.update_yaxes(visible=False, secondary_y=True)
    fig1.update_layout(xaxis_rangeslider_visible=True)  # You can also hide the range slider.
    
    new_start_date = df_stock_data.index.min().strftime("%Y-%m-%d")
    new_end_date = df_stock_data.index.max().strftime("%Y-%m-%d")
    chart_title = f'{stock_ticker} Price Candlestick Graph\n(from {new_start_date} to {new_end_date}, {df_stock_data.shape})'
    fig1.update_layout(title=chart_title)  # Update this line

    plt.title(chart_title)
    path_image_save = path_image_save.replace('.png', '_2-candlestick_.png')
    fig1.write_image(path_image_save)  # Update this line
    #fig1.show()



# SPP-1_
def clean_stockprice_data(df_stock_data):
    print('\n[clean_stockprice_data]')
    df_stock_data = df_stock_data[df_stock_data['Volume'] != 0]  # Remove rows with empty volume.
    if 'MACD_Signal' in df_stock_data.columns:
        # If the column 'MACD_Signal' exists, remove missing rows in that column.
        df_stock_data.dropna(subset=['MACD_Signal'], inplace=True)
    else:
        print('Column MACD_Signal does not exist. There are currenly', df_stock_data.shape[1], 'columns.')
    print('--[Shape]', df_stock_data.shape, end='\n\n')
    return df_stock_data

# SPP-1_
def calculate_statistical_analysis(df_stock_data):
    print('\n[calculate_statistical_analysis]')
    import ta
    # Calculate Moving Averages
    df_stock_data['SMA_10'] = ta.trend.sma_indicator(df_stock_data['Close'], window=10)
    df_stock_data['EMA_10'] = ta.trend.ema_indicator(df_stock_data['Close'], window=10)

    # Calculate RSI
    df_stock_data['RSI'] = ta.momentum.rsi(df_stock_data['Close'], window=14)

    # Calculate MACD
    macd = ta.trend.MACD(df_stock_data['Close'])
    df_stock_data['MACD'] = macd.macd()
    df_stock_data['MACD_Signal'] = macd.macd_signal()
    df_stock_data['MACD_Hist'] = macd.macd_diff()

    # Calculate Bollinger Bands
    bollinger = ta.volatility.BollingerBands(df_stock_data['Close'], window=20, window_dev=2)
    df_stock_data['Bollinger_High'] = bollinger.bollinger_hband()
    df_stock_data['Bollinger_Low'] = bollinger.bollinger_lband()
    df_stock_data['Bollinger_BW'] = df_stock_data['Bollinger_High'] - df_stock_data['Bollinger_Low']
    print('--[Shape]', df_stock_data.shape, end='\n\n')
    return df_stock_data



def list_all_sheets_in_excel(path_excel):
    print('\n[list_all_sheets_in_excel]')
    workbook = openpyxl.load_workbook(path_excel)
    list_sheet_names = workbook.sheetnames
    print('--[list_sheet_names]', list_sheet_names, end='\n\n')
    return list_sheet_names


# SPP-5_
def prepare_training_data_and_scale(df_stock_data, time_step, future_step):
    print('\n[prepare_training_data_and_scale]')
    from sklearn.preprocessing import StandardScaler,  MinMaxScaler
    from sklearn.compose import ColumnTransformer
    X, Y = [], []
    for i in range(len(df_stock_data) - time_step - future_step + 1):
        X.append(df_stock_data.iloc[i:(i + time_step)].values)
        Y.append(df_stock_data.iloc[i + time_step:i + time_step + future_step, :4].values)
    # Convert X and Y to numpy arrays
    X, Y = np.array(X), np.array(Y)
    # Initialize scalers
    X_standard_scaler = StandardScaler()
    Y_minmax_scaler = MinMaxScaler()
    # Reshape for scaling
    X_reshaped = X.reshape(-1, X.shape[-1])  # Flatten time steps, keep features
    Y_reshaped = Y.reshape(-1, Y.shape[-1])  # Flatten future steps, keep features
    # Look for binary columns
    feature_columns = list(df_stock_data.columns.values)
    num_of_features = len(feature_columns)
    print('--[num_of_features]:', num_of_features)
    columns_to_scale = list(range(0, num_of_features))
    print('--[columns_to_scale]:', columns_to_scale)
    # [columns_to_scale]: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31]
    # This part remove the columns with binary values (them contain 'exist' in the column header) that we don't want to scale. 
    columns_removed = []
    for index, iter_col in  enumerate(feature_columns):
        if 'exist' in iter_col:
            columns_to_scale.remove(index)
            columns_removed.append(index)
    print('--[columns_to_scale]:', columns_to_scale)
    # [columns_to_scale]: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30]
    # Apply scaling
    X_col_trans = ColumnTransformer([
        ('scale', X_standard_scaler, columns_to_scale)
        ], remainder='passthrough')
    X_scaled = X_col_trans.fit_transform(X_reshaped).reshape(X.shape)
    # ColumnTransformer move the uscaled columns all to the end, now we have to move them back.
    for col in columns_removed:
        num_col_removed = len(columns_removed)
        if col != num_of_features:
            wrong_col_pos = num_of_features - num_col_removed + 1
            temp = X_scaled[:, :, wrong_col_pos].copy()                # Create a temporary array to hold the values of the last index in the third dimension
            X_scaled[:, :, col+1:wrong_col_pos] = X_scaled[:, :, col:wrong_col_pos-1]   # Shift elements from index 15 to 30 one position forward
            X_scaled[:, :, col] = temp                       # Place the values from the temporary array into index 15
            Y_scaled = Y_minmax_scaler.fit_transform(Y_reshaped)
    
    return X_scaled, Y_scaled, X_col_trans, Y_minmax_scaler, columns_to_scale

    """
    Previous easy code
    temp = X_scaled[:, :, 31].copy()                # Create a temporary array to hold the values of the last index in the third dimension
    X_scaled[:, :, 16:31] = X_scaled[:, :, 15:30]   # Shift elements from index 15 to 30 one position forward
    X_scaled[:, :, 15] = temp                       # Place the values from the temporary array into index 15
    Y_scaled = Y_minmax_scaler.fit_transform(Y_reshaped)
    """


    
def plot_model_png(path_model, model_plot_name = 'model_plot.png'):
    from keras.models import load_model
    from keras.utils import plot_model
    # Load saved mode from mode_plot_path and plot_model
    model = load_model(path_model)
    path_model_plot_png = os.path.join(path_model, model_plot_name)
    plot_model(model, to_file=path_model_plot_png, show_shapes=True, show_layer_names=True)
    return path_model_plot_png

#SPP-7_
def add_one_future_day(pd_index_dates):
    print('\n[add_one_future_day]')
    last_date = pd_index_dates[-1]  # Directly access the last date
    next_date = last_date + timedelta(days=1)  # Add one day
    print('--The next_date added is:', next_date)
    new_index = pd_index_dates.append(pd.Index([next_date]))
    return new_index

def plot_training_history_PTH(train_losses, val_losses, lr_rates, str_train_settings, path_history_plot_save):
    print('\n[plot_training_history]')
    import matplotlib.pyplot as plt
    # Create a figure and a set of subplots
    fig, ax1 = plt.subplots(figsize=(12, 9))
    # Plot training & validation loss values
    ax1.plot(train_losses, color = 'royalblue', label='Training Loss', linewidth=3)
    ax1.plot(val_losses, color = 'darkorange', label='Validation Loss', linewidth=3)
    ax1.set_title('Model Loss')
    ax1.set_xlabel('Epoch')
    ax1.set_ylim(0, 0.01)
    ax1.set_ylabel('Training Loss')
    # Plot the learning rate schedule
    ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis
    ax2.plot(lr_rates, color = 'forestgreen', label='Learning Rate')
    ax2.set_ylim(1e-06, 1e-01)
    ax2.set_yscale("log")
    ax2.set_ylabel('Scheduled Learning Rate')  # we already handled the x-label with ax1
    # Combine legends
    handles1, labels1 = ax1.get_legend_handles_labels()
    handles2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(handles1 + handles2, labels1 + labels2, loc='upper left')
    # Add text
    ax2.text(0.4, 0.98, str_train_settings
             , transform=ax2.transAxes
             , fontsize=10
             , verticalalignment='top'
             , horizontalalignment='left'
             , fontname='monospace')  # Add learning rate text
    # Save the plot to the specified path
    plt.savefig(path_history_plot_save)
    # plt.show()
    return fig


def plot_training_history_TF(training_history, str_train_settings, path_history_plot_save):
    print('\n[plot_training_history]')
    import matplotlib.pyplot as plt
    # Create a figure and a set of subplots
    fig, ax1 = plt.subplots(figsize=(12, 9))
    # Plot training & validation loss values
    ax1.plot(training_history.history['loss'], color = 'royalblue', label='Train Loss', linewidth=3)
    ax1.plot(training_history.history['val_loss'], color = 'darkorange', label='Validation Loss', linewidth=3)
    ax1.set_title('Model Loss')
    ax1.set_xlabel('Epoch')
    ax1.set_ylim(0, 0.1)
    ax1.set_ylabel('Loss')
    # Plot the learning rate schedule
    ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis
    ax2.plot(training_history.history['lr'], color = 'forestgreen', label='Learning Rate')
    ax2.set_ylim(0, 0.01)
    ax2.set_ylabel('Scheduled Learning Rate')  # we already handled the x-label with ax1
    # Combine legends
    handles1, labels1 = ax1.get_legend_handles_labels()
    handles2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(handles1 + handles2, labels1 + labels2, loc='upper left')
    # Add text
    ax2.text(0.5, 0.98, str_train_settings
             , transform=ax2.transAxes
             , fontsize=10
             , verticalalignment='top'
             , horizontalalignment='left'
             , fontname='monospace')  # Add learning rate text
    # Save the plot to the specified path
    plt.savefig(path_history_plot_save)
    # plt.show()
    return fig


# SPP-5_
class StockPriceLSTM(nn.Module):
    # Initialization
    def __init__(self, input_dim, hidden_dim, layer_dim, output_dim):
        super(StockPriceLSTM, self).__init__()
        self.hidden_dim = hidden_dim
        self.layer_dim = layer_dim
        self.lstm = nn.LSTM(input_dim, hidden_dim, layer_dim, batch_first=True) # LSTM Layer
        self.fc = nn.Linear(hidden_dim, output_dim)  # Output. Predicting output_dim=4 value.

    def forward(self, x):
        # Initialize hidden state and cell state with zeros
        h0 = torch.zeros(self.layer_dim, x.size(0), self.hidden_dim).requires_grad_()
        c0 = torch.zeros(self.layer_dim, x.size(0), self.hidden_dim).requires_grad_()
        # Detach tensor from computation as we are making a new forward pass
        out, (hn, cn) = self.lstm(x, (h0.detach(), c0.detach()))
        # Index hidden state of last time step
        out = self.fc(out[:, -1, :]) 
        return out



"""model_name = 'model_' + str(training_datetime_tag) + '_Data' + str(shape_training_data[0]) + '-' + str(shape_training_data[1]) \
            + '_LSTM_Ts'  + str(time_step) + ', Fs' + str(future_step) \
            + ', nIF' + str(num_input_features)+ ', nOF' + str(num_output_features) \
            + '_Hs' + str(hidden_size) + ', nL' + str(num_layers) \
            + ', Bs' + str(batch_size) + ', Ep' + str(num_epoch) + '.pth'
path_model = os.path.join(dir_model, model_name)"""

#model_2023-12-09_170602_Data468-32_LSTM_Ts30, Fs1, nIF32, nOF4_Hs40, nL2, Bs16, Ep100.pth

# SPP-7_
def extract_info_from_model_path(path_model):
    print('\n[extract_info_from_model_path]')
    basename = os.path.basename(path_model)
    print('--[basename]:', basename)
    training_datetime_tag = basename.split('model_')[1].split('_Data')[0]
    shape_training_data = basename.split('_Data')[1].split('_LSTM_Ts')[0]
    time_step = basename.split('_Ts')[1].split(', Fs')[0]
    future_step = basename.split(', Fs')[1].split(', nIF')[0]
    num_input_features = basename.split(', nIF')[1].split(', nOF')[0]
    num_output_features = basename.split(', nOF')[1].split('_Hs')[0]
    hidden_size = basename.split('_Hs')[1].split(', nL')[0]
    num_layers = basename.split(', nL')[1].split(', Bs')[0]
    batch_size = basename.split(', Bs')[1].split(', Ep')[0]
    num_epoch = basename.split(', Ep')[1].split('_1-model.pth')[0]

    dic_model_info = {
        'training_datetime_tag': training_datetime_tag,
        'shape_training_data': shape_training_data,
        'time_step': time_step,
        'future_step': future_step,
        'num_input_features': num_input_features,
        'num_output_features': num_output_features,
        'hidden_size': hidden_size,
        'num_layers': num_layers,
        'batch_size': batch_size,
        'num_epoch': num_epoch,
    }
    print('--[dic_model_info]:', dic_model_info, end='\n\n')
    return dic_model_info


# SPP-5_, SPP-7_
#[] Convert array to tensor
class StockDataset(Dataset):
    def __init__(self, X, Y):
        self.X = torch.tensor(X, dtype=torch.float32)  # Converting to PyTorch tensor
        self.Y = torch.tensor(Y, dtype=torch.float32)  # Converting to PyTorch tensor
    def __len__(self):
        return len(self.X)
    def __getitem__(self, idx):
        return self.X[idx], self.Y[idx]
    
    
 # SPP-3_, SPP-7_   
def inverse_transform_with_CT(X_scaled, ct, columns_to_scale):
    # Flattening is necessary to apply inverse_transform on 2D array
    num_samples, num_timesteps, num_features = X_scaled.shape
    X_scaled_flat = X_scaled.reshape(-1, num_features)
    X_inv_flat = np.zeros_like(X_scaled_flat)
    # Get the transformer for the scaled columns
    transformer = ct.named_transformers_['scale']
    # Inverse transform the scaled columns
    X_inv_flat[:, columns_to_scale] = transformer.inverse_transform(X_scaled_flat[:, columns_to_scale])
    # Fill in the unscaled columns
    for col in range(num_features):
        if col not in columns_to_scale:
            X_inv_flat[:, col] = X_scaled_flat[:, col]
    # Reshape back to original 3D shape
    X_inv = X_inv_flat.reshape(num_samples, num_timesteps, num_features)
    
    return X_inv


 # SPP-7_, SPP-8_  
def add_one_more_row_using_average(df_latest):
    next_date = df_latest.index[-1] + pd.Timedelta(days=1)
    average_values = df_latest.mean()
    new_row = pd.DataFrame([average_values], index=[next_date])
    df_latest = pd.concat([df_latest, new_row])
    return df_latest



def add_date_index_col_for_array_predicted(df_latest, array_predicted, time_step):
    print('\n[add_date_index_col_for_array_predicted')
    list_index_large = df_latest.index.tolist()
    len_index_large = len(list_index_large)
    len_index_small = array_predicted.shape[0]
    print('--[list_col_index_truncated] (first, last):'
        , list_index_large[0], ','
        , list_index_large[-1:][0])
    print('--[len_index_large]:', len_index_large)
    index_ct_back = len_index_small
    list_col_index_truncated = list_index_large[-index_ct_back:]
    print('--[list_col_index_truncated] (first, last):'
        , list_col_index_truncated[0], ','
        , list_col_index_truncated[-1:][0])
    date_col_truncated_length = len(list_col_index_truncated)
    print('--[date_col_truncated_length]:', date_col_truncated_length, end='\n\n')
    df_predictions = None
    if len(list_col_index_truncated) == len(array_predicted):
        df_predictions = pd.DataFrame(array_predicted, 
                                    columns=['Predicted_Open', 'Predicted_High', 'Predicted_Low', 'Predicted_Close'],
                                    index=pd.Index(list_col_index_truncated, name='Date'))
    else:
        print("Error: The length of the index list does not match the number of rows in the array.")
        
    return df_predictions












"""
Function to save matrix in a visualizeing way for CV homework.
Might need it here some day.

"""

def visualize_matrix_save(matrix, path, dpi=300):
    nrows, ncols = matrix.shape
    fig_size = (max(nrows, 5) * 0.5, max(ncols, 5) * 0.5)
    plt.figure(figsize=fig_size, dpi=dpi)
    max_abs_val = np.max(np.abs(matrix))  # Find maximum of absolute value.
    plt.imshow(matrix, cmap='seismic', vmin=-max_abs_val, vmax=max_abs_val)
    # Optionally add gridlines for very small matrices
    if nrows <= 5 and ncols <= 5:
        plt.grid(which='major', color='black', linestyle='-', linewidth=2)
    # Matrix statistics
    stat_max, stat_min, stat_mean, stat_med = round(np.max(matrix),3), round(np.min(matrix),3), round(np.mean(matrix),3), round(np.median(matrix),3)
    stats_text = f'Shape: {nrows} × {ncols}\nMax: {stat_max},  Min: {stat_min}\nMean: {stat_mean},  Median: {stat_med}'
    plt.text(0, -ncols//10, stats_text, fontsize=8, color='white', bbox=dict(facecolor='black', alpha=0.5))
    plt.axis('off')
    plt.savefig(path, dpi=dpi, bbox_inches='tight', pad_inches=0.1)
    plt.close()
    