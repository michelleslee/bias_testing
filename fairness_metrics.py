import dash_html_components as html
fairness_metrics = [{
    'name':'Equal Opportunity',
    'description': """Equal opportunity / False negative error rate balance: A classifier satisfies this definition if 
                      both groups have the same false negative rate.
                      For example, the probability of someone with an actually good credit score being incorrectly assigned a bad credit score 
                      should be the same for both male and female applicants. The idea behind this classifier is that 
                      it should give similar predictions for applicants with actually positive credit scores. """,
    'link':html.Label([html.A('Source', href='https://arxiv.org/pdf/1610.07524.pdf')]),
    'tag':'equal_opp'
},{
    'name':'Predictive Equality',
    'description': """Predictive Equality / False positive error rate balance: A classifier satisfies this definition if both groups have the same false positive rate.
                      For example, among applicants with actually bad credit scores, the probability of being incorrectly assigned a good 
                      predicted credit score should be the same for both male and female applicants. The idea behind this classifier is that 
                      it should give similar results for applicants with actually negative credit scores. """,
    'link':html.Label([html.A('Source', href='https://arxiv.org/pdf/1610.07524.pdf')]),
    'tag':'predictive_equality'
},{    
    'name':'Equalised Odds',
    'description': """Equalised odds / conditional procedure accuracy equality / disparate mistreatment: 
                      A classifier satisfies this definition if both groups have the same false negative and false positive rates,
                      which is mathematically equivalent to having equal true positive and false positive rates.
                      Combining Equal Opportunity and Predictive Equality, the probability of an applicant with a good credit score
                      being predicted as credit-worthy is the same, and the probability of an applicant with a bad credit score
                      being predicted as not credit-worthy is also the same, regardless of gender. """,
    'link':html.Label([html.A('Source', href='http://fairware.cs.umass.edu/papers/Verma.pdf')]),
    'tag':'equalised_odds'
},{
    'name':'Predictive Parity',
    'description': """Predictive parity / outcome test: A classifier satisfies this definition if both groups have the same positive predictive value. 
                      Among applicants with actually good credit scores (positive predictive value), the probability of predicting a good credit score
                      is the same regardless of gender.""",
    'link':html.Label([html.A('Source', href='http://fairware.cs.umass.edu/papers/Verma.pdf')]),
    'tag':'predictive_parity'
},{
    'name':'Treatment Equality',
    'description': """Treatment equality: A classifier satisfies this metric if both classes have a equal ratio of false negative and false
                      positive rates. For example, if a smaller number of male applicants are incorrectly predicted as non-creditworthy, 
                      and/or larger number of male applicants are incorrectly predicted as creditworthy, then the classifier fails this test.""",
    'link':html.Label([html.A('Source', href='http://fairware.cs.umass.edu/papers/Verma.pdf')]),
    'tag':'treatment_equality'
},{
    'name':'Balance for Positive class',
    'description': """Positive class balance: A classifier satisfies this score if both groups with actual positive outcomes have equal average probability score.
                      For example, if credit-worthy male applicants consistently receive a higher probability score
                      than credit-worthy women, then the classifier fails the test.""",
    'link':html.Label([html.A('Source', href='http://fairware.cs.umass.edu/papers/Verma.pdf')]),
    'tag':'positive_class_balance'
},{
    'name':'Balance for Negative class',
    'description': """A classifier satisfies this score if both groups with actual negative outcomes have equal average probability score. 
                      Non-credit-worthy male and female applicants should receive the same probability score.""",
    'link':html.Label([html.A('Source', href='http://fairware.cs.umass.edu/papers/Verma.pdf')]),
    'tag':'negative_class_balance'
}]


introduction_text = [html.H1('AI Auditing Tool: Fairness test results'),
                   f"""This report outlines the test results of your algorithm against some of the most commonly cited definitions of fairness.
                       Please note that it is mathematically impossible to satisfy all fairness conditions. """,
                        html.Label([html.A('Source', href='https://arxiv.org/abs/1609.05807')]),
                    """The tests below are intended as an initial test to reveal any potential biases in your predictions and outcomes.
                       Further analysis, including other tests (e.g. counterfactual fairness), is available upon request.
                    """]