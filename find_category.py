import bisect
import ipdb

# Define percentile category thresholds (upper bounds of each interval)
percentile_categories = [0.015, 0.025, 0.035, 0.045, 0.055, 0.065, 0.075, 0.085, 0.095, 
                         0.105, 0.115, 0.125, 0.135, 0.145, 0.155, 0.165, 0.175, 0.185, 0.195, 
                         0.205, 0.215, 0.225, 0.235, 0.245, 0.255, 0.265, 0.275, 0.285, 0.295, 
                         0.305, 0.315, 0.325, 0.335, 0.345, 0.355, 0.365, 0.375, 0.385, 0.395, 
                         0.405, 0.415, 0.425, 0.435, 0.445, 0.455, 0.465, 0.475, 0.485, 0.495, 
                         0.505, 0.515, 0.525, 0.535, 0.545, 0.555, 0.565, 0.575, 0.585, 0.595, 
                         0.605, 0.615, 0.625, 0.635, 0.645, 0.655, 0.665, 0.675, 0.685, 0.695, 
                         0.705, 0.715, 0.725, 0.735, 0.745, 0.755, 0.765, 0.775, 0.785, 0.795, 
                         0.805, 0.815, 0.825, 0.835, 0.845, 0.855, 0.865, 0.875, 0.885, 0.895, 
                         0.905, 0.915, 0.925, 0.935, 0.945, 0.955, 0.965, 0.975, 0.985, 0.995]

def find_percentile_category(value, categories):
    """Finds the percentile category interval (open on left, closed on right) that covers the value."""
    index = bisect.bisect_right(categories, value)
    ipdb.set_trace()
    if index == 0 or index > len(categories):  # Out of range cases
        return None  
    lower_bound = 0.005 if index == 1 else categories[index - 2]  # Compute lower bound
    upper_bound = categories[index - 1]  # Upper bound from list
    return (lower_bound, upper_bound)

# Test cases
values = [0.01, 0.02, 0.5, 0.99, 0.985, 0.75]
for v in values:
    print(f"Value: {v}, Percentile Category: {find_percentile_category(v, percentile_categories)}")
