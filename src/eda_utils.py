import matplotlib.pyplot as plt
import seaborn as sns

def plot_dist_with_central_tendency(df, column, title):
    plt.figure(figsize=(10, 5))
    sns.histplot(df[column], kde=True, color='steelblue', bins=30)
    
    mean_val = df[column].mean()
    median_val = df[column].median()
    
    plt.axvline(mean_val, color='red', linestyle='--', linewidth=2, label=f'Mean: {mean_val:.2f}')
    plt.axvline(median_val, color='green', linestyle='-', linewidth=2, label=f'Median: {median_val:.2f}')
    
    plt.title(title, fontsize=14)
    plt.xlabel(column)
    plt.ylabel('Frekuensi')
    plt.legend()
    plt.grid(axis='y', alpha=0.3)
    plt.show()