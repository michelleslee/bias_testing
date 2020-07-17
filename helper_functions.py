
import pandas as pd
import numpy as np
from sklearn.metrics import confusion_matrix

def get_classes(df, protected_feature):
    df = df.sort_values(by=[protected_feature])
    classes = df[protected_feature].unique()
    return classes[~pd.isnull(classes)]

def create_confusion_matrix(df, class_, protected_feature, actual_outcome, predicted_outcome):
    tmp_df = df[df[protected_feature]==class_]
    return confusion_matrix(tmp_df[actual_outcome],tmp_df[predicted_outcome]).ravel()

def create_metric_dict(true_negative, false_positive, false_negative, true_positive):
    metrics= {}
    metrics['true_negative'] = true_negative
    metrics['false_positive'] = false_positive
    metrics['false_negative'] = false_negative
    metrics['true_positive'] = true_positive
    metrics['true_positive_rate'] = np.round( true_positive/(true_positive+false_negative),2 )
    metrics['true_negative_rate'] = np.round( true_negative/(false_positive+true_negative),2 )
    metrics['false_positive_rate'] = np.round( false_positive/(false_positive+true_negative),2 )
    metrics['false_negative_rate'] = np.round( false_negative/(true_positive+false_negative),2 )
    metrics['positive_predictive_value'] = np.round( true_positive/(true_positive+false_positive),2 )
    return metrics

def create_prob_dict(df, class_, protected_feature, actual_outcome, positive_class, probability):
    tmp_df = df[df[protected_feature]==class_]
    probability_ = {}
    tmp = tmp_df[tmp_df[actual_outcome] == positive_class]
    probability_['positive_class_balance'] = np.round(np.mean(tmp[probability]),2)
    tmp = tmp_df[tmp_df[actual_outcome] != positive_class]
    probability_['negative_class_balance'] = np.round(np.mean(tmp[probability]),2)
    return probability_

def create_fairness_dict(metric_dict, baseline_metric, prob_dict=None, baseline_prob=None):
    fairness_dict = {}
    fairness_dict['equal_opp'] = (metric_dict['true_negative_rate'] - 
                                  baseline_metric['true_negative_rate'])
    
    fairness_dict['predictive_equality'] = (metric_dict['false_positive_rate'] - 
                                            baseline_metric['false_positive_rate'])
    
    fairness_dict['predictive_parity'] = (metric_dict['positive_predictive_value'] - 
                                          baseline_metric['positive_predictive_value'])
    
    fairness_dict['treatment_equality'] = (metric_dict['false_negative']/metric_dict['false_positive'] - 
                                           baseline_metric['false_negative']/baseline_metric['false_positive'])
    
    if prob_dict != None and baseline_prob != None:
        fairness_dict['positive_class_balance'] = prob_dict['positive_class_balance'] - baseline_prob['positive_class_balance']
        fairness_dict['negative_class_balance'] = prob_dict['negative_class_balance'] - baseline_prob['negative_class_balance']
    return fairness_dict

def generate_class_fairness(df, protected_feature, baseline_group, 
                            classes, actual_outcome, predicted_outcome, positive_class, probability):
    tn, fp, fn, tp = create_confusion_matrix(df, baseline_group, protected_feature, actual_outcome, predicted_outcome)
    baseline_metric = create_metric_dict(tn, fp, fn, tp)
    baseline_prob = create_prob_dict(df, baseline_group, protected_feature, actual_outcome, positive_class, probability)

    class_fairness = {}
    class_fairness['confusion_metrics'] ={}
    for class_ in classes:
        metric = create_metric_dict(tn, fp, fn, tp)
        class_fairness['confusion_metrics'][class_] = metric
        if class_ != baseline_group:
            probability_ = create_prob_dict(df, class_, protected_feature, actual_outcome, positive_class, probability)
            tn, fp, fn, tp = create_confusion_matrix(df, class_, protected_feature, actual_outcome, predicted_outcome)
            class_fairness[class_] = create_fairness_dict(metric, baseline_metric, probability_, baseline_prob)
        

    return class_fairness