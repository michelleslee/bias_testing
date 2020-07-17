from AI_Bias_Dash import get_page_stats
import pandas as pd



df = pd.read_excel('hiring_data_with_predictions.xlsx')
df = df.applymap(lambda s:s.capitalize().strip() if type(s) == str else s)
ao = 'hired'
pc = 'Yes'
prob = 'probability'
po = 'predicted'
pf = 'gender'
bg = 'Male'
error = 5
get_page_stats(df,ao,pc,prob,po,pf,bg,error)

# df = pd.read_excel('compass/compas-scores-raw.xlsx')
# df = df.applymap(lambda s:s.capitalize().strip() if type(s) == str else s)
# ao = 'RecSupervisionLevelText'
# pc = 'Low'
# prob = None
# po = 'RawScore'
# pf = 'Ethnic_Code_Text'
# bg = 'Caucasian'
# error = 5
# get_page_stats(df,ao,pc,prob,po,pf,bg,error)
# test_list = ['Female', 'Male', 'Other', 'Pfns']

# for i, name_ in enumerate(test_list):
#     print()
#     print(name_)


# def get_error_delta(value, error):
#     if value % error == value:
#         return 0
#     else:
#         return value % error


# print(get_error_delta(5, 10))
