import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

def performance():
    labels = ['True Positives', 'False Positives', 'False Negatives', 'True Negatives']
    sizes = [45, 9, 186, 8]
    colors = ['#4CAF50', '#FFC107', '#F44336', '#2196F3']

    plt.figure(figsize=(8,6))
    plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=140)
    plt.title('Model Prediction Distribution (n=248)')
    plt.savefig('performance_metrics.png', dpi=300, bbox_inches='tight')



def Hallucination():
    categories = ['RiskID', 'RiskDesc', 'VulnID', 'VulnDesc']
    rates = [81.45, 81.05, 98.39, 97.98]

    plt.figure(figsize=(10,6))
    ax = sns.barplot(x=categories, y=rates, palette="rocket")
    #plt.title('Hallucination Rates by Type')
    plt.ylabel('Percentage (%)')
    plt.ylim(0, 100)

    for p in ax.patches:
        ax.annotate(f'{p.get_height():.1f}%', 
                    (p.get_x() + p.get_width() / 2., p.get_height()),
                    ha='center', va='center', 
                    xytext=(0, 9), 
                    textcoords='offset points')

    plt.savefig('hallucination_rates.png', dpi=300, bbox_inches='tight')

def precision_Recall():   

    thresholds = [0.6, 0.7, 0.8, 0.9]
    precision = [75, 80, 83, 85]
    recall = [60, 45, 30, 15]

    plt.figure(figsize=(10,6))
    plt.plot(thresholds, precision, 'go-', label='Precision')
    plt.plot(thresholds, recall, 'bo-', label='Recall')
    plt.axvline(x=0.7, color='r', linestyle='--', label='Current Threshold')
    #plt.title('Precision-Recall')
    plt.xlabel('Confidence Threshold')
    plt.ylabel('Percentage (%)')
    plt.legend()
    plt.grid(True)
    plt.savefig('precision_recall.png', dpi=300)
    
    
def error_compare():
    error_types = ['False Negatives', 'False Positives', 'Hallucinated Details']
    counts = [186, 9, 202]
    explode = (0.1, 0, 0.1)

    plt.figure(figsize=(8,6))
    plt.pie(counts, labels=error_types, 
            autopct='%1.1f%%')
    plt.title('Error Composition (n=195 errors)')
    plt.savefig('error_types.png', dpi=300)
    
if __name__ == "__main__":
    #performance()
    #Hallucination()
    #precision_Recall()
    error_compare()