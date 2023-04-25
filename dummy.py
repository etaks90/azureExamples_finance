# https://webpages.charlotte.edu/mirsad/itcs6265/group1/domain.html#:~:text=The%20Berka%20dataset%20is%20a,clients%20with%20approximately%201%2C000%2C000%20transactions.

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import pickle

#############################################################################################################################
################################################  READ FILES    #############################################################
#############################################################################################################################

# account
df_account = pd.read_csv(r"C:\Users\oliver.koehn\Documents\gitProjects\azureExamples_finance\eval_berka\in\account.asc", delimiter=";")
df_account["acc_dist_id"] = df_account["district_id"]
df_account['date'] = pd.to_datetime("19" + df_account['date'].astype(str), format='%Y-%m-%d')
df_account = df_account.rename(columns={'date': 'date_acc'})

# card
df_card = pd.read_csv(r"C:\Users\oliver.koehn\Documents\gitProjects\azureExamples_finance\eval_berka\in\card.asc", delimiter=";")
df_card['issued'] = pd.to_datetime("19" + df_card['issued'].astype(str), format='%Y-%m-%d')
df_card = df_card.rename(columns={'type': 'card_type'})

# client
df_client = pd.read_csv(r"C:\Users\oliver.koehn\Documents\gitProjects\azureExamples_finance\eval_berka\in\client.asc", delimiter=";")
df_client["cli_dist_id"] = df_client["district_id"]
df_client["MM"] = df_client['birth_number']//100 - df_client['birth_number']//10000*100
df_client['gender'] = 'M'
# it sa strang eformat where gende ris encoded like this
df_client.loc[df_client['MM']>50,'gender'] = 'F'
df_client.loc[df_client['gender']=='F','birth_number'] -= 5000
df_client['birth_number'] = pd.to_datetime("19" + df_client['birth_number'].astype(str), format='%Y-%m-%d')
df_client.rename(columns = {'birth_number':'date_birth'}, inplace=True)
df_client.drop('MM',1,inplace=True)

# disp
df_disp = pd.read_csv(r"C:\Users\oliver.koehn\Documents\gitProjects\azureExamples_finance\eval_berka\in\disp.asc", delimiter=";")
df_disp = df_disp.rename(columns={'type': 'disp_type'})

# district
df_district = pd.read_csv(r"C:\Users\oliver.koehn\Documents\gitProjects\azureExamples_finance\eval_berka\in\district.asc", delimiter=";")
df_district = df_district.rename(columns={'A1': 'district_id'})

# loan
df_loan = pd.read_csv(r"C:\Users\oliver.koehn\Documents\gitProjects\azureExamples_finance\eval_berka\in\loan.asc", delimiter=";")
df_loan['date'] = pd.to_datetime("19" + df_loan['date'].astype(str), format='%Y-%m-%d')
df_loan = df_loan.rename(columns={'date': 'date_loan'})

# order
df_order = pd.read_csv(r"C:\Users\oliver.koehn\Documents\gitProjects\azureExamples_finance\eval_berka\in\order.asc", delimiter=";")
df_order = df_order.rename(columns={'amount': 'order_amount'})
df_order['order_amount'] = df_order.order_amount.astype('float')
df_order_average = df_order.copy()
df_order_average = df_order_average.groupby('account_id').mean()
df_order_average = df_order_average.rename(columns={'order_amount': 'average_order_amount'})
df_order_average = df_order_average[["order_id", "average_order_amount"]]

# trans
df_trans = pd.read_csv(r"C:\Users\oliver.koehn\Documents\gitProjects\azureExamples_finance\eval_berka\in\trans.asc", delimiter=";")
df_trans['date'] = pd.to_datetime("19" + df_trans['date'].astype(str), format='%Y-%m-%d')
df_trans_average = df_trans.copy()
df_trans_average = df_trans_average.groupby('account_id').mean()
df_trans_average["account_id"] = df_trans_average.index
df_trans_average = df_trans_average.rename(columns={'amount': 'average_trans_amount', 'balance': 'average_trans_balance'})
df_trans_average = df_trans_average[['average_trans_amount', 'average_trans_balance']]
df_n_trans = df_trans.groupby('account_id').count()
df_n_trans = df_n_trans.rename(columns={'trans_id': 'n_trans'})
df_n_trans = df_n_trans[["n_trans"]]

#############################################################################################################################
################################################      JOIN      #############################################################
#############################################################################################################################


df = df_loan.merge(df_account, on = "account_id", how = "inner")\
    .merge(df_district, on = "district_id", how = "inner")\
    .merge(df_order_average, on = "account_id", how = "inner")\
    .merge(df_trans_average, on = "account_id", how = "inner")\
    .merge(df_disp, on = "account_id", how = "inner")\
    .merge(df_card, on = "disp_id", how = "left")\
    .merge(df_client, on = "client_id", how = "inner")\
    .merge(df_n_trans, on = "account_id", how = "inner")\

df = df[df["disp_type"] == "OWNER"]

# additional fields
df['days_between'] = (df['date_loan'] - df['date_acc']).dt.days
df['n_inhabitants'] = df.A4
df['average_salary'] = df.A11
df['average_unemployment_rate'] = df[['A12', 'A13']].mean(axis=1)
df['entrepreneur_rate'] = df['A14']
df['average_crime_rate'] = df[['A15', 'A16']].mean(axis=1) / df['n_inhabitants']
df['default'] = (df['status'] == 'B') | (df['status'] == 'D')

df['same_district'] = df['acc_dist_id'] == df['cli_dist_id']
df['date_opening_loan'] = pd.to_datetime(df['date_loan'], format='%Y-%m-%d')
df['owner_age_at_opening'] = (df['date_opening_loan']  - df['date_birth']).dt.days // 365

cat_cols = ["frequency", "card_type", "gender"]
num_cols = ['amount', 'duration', 'payments', 'days_between', 'n_inhabitants', 
            'average_salary', 'average_unemployment_rate', 'entrepreneur_rate', 
            'average_crime_rate', 'average_order_amount', 'average_trans_amount',
            'average_trans_balance', 'n_trans', 'owner_age_at_opening', 
            'same_district']
list_features = num_cols + cat_cols

df[list_features]

print(len(df))