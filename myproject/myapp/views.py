from django.shortcuts import render, redirect # Pour rendre des templates HTML et rediriger l'utilisateur.
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from io import BytesIO  # Pour manipuler des flux en mémoire (comme des fichiers) sans les enregistrer sur disque
import base64 # Pour encoder les graphiques en base64 afin de les afficher dans des templates HTML
import numpy as np
from django.urls import reverse # Génération d'URLs dynamiques
#render remplace les parties dynamiques par les données fournies
def upload_file(request):
    if request.method == 'POST' and request.FILES.get('file'):
        try:
            file = request.FILES['file']
            if file.name.endswith('.csv'):
                df = pd.read_csv(file)
                request.session['df_json'] = df.to_json() # Sauvegarde le DataFrame en JSON dans la session
                return redirect('analyze') # Redirige vers la vue d'analyse.
            else:
                return render(request, 'upload.html', {'error': 'Veuillez uploader un fichier CSV'})
        except Exception as e:
            return render(request, 'upload.html', {'error': f'Erreur lors du traitement du fichier: {str(e)}'})
    return render(request, 'upload.html')

def analyze_data(request):
    if 'df_json' not in request.session: # Vérifie si les données sont dans la session.
        return redirect('upload')
    
    try:
        df = pd.read_json(request.session['df_json']) # Charge les données sauvegardées dans la session.
        
        # Informations détaillées sur le dataset
        analysis = {
            'shape': df.shape,
            'head': df.head().to_html(classes='table table-striped'),
            'tail': df.tail().to_html(classes='table table-striped'),
            'missing_values': df.isnull().sum().to_dict(),
            'columns': df.columns.tolist(),
            'numeric_columns': df.select_dtypes(include=[np.number]).columns.tolist(),
            'categorical_columns': df.select_dtypes(include=['object']).columns.tolist(),
            'dtypes': df.dtypes.to_dict(),
            'total_missing': df.isnull().sum().sum(),
            'percent_missing': (df.isnull().sum().sum() / (df.shape[0] * df.shape[1]) * 100).round(2)
        }

        # Informations sur les valeurs uniques et fréquences
        value_counts = {}
        for col in df.columns:
            value_counts[col] = {
                'unique_count': df[col].nunique(),
                'value_counts': df[col].value_counts().to_dict(),
                'top_values': df[col].value_counts().head(5).to_dict(),
                'missing_count': df[col].isnull().sum(),
                'missing_percentage': (df[col].isnull().sum() / len(df) * 100).round(2)
            }
        
        # Statistiques descriptives pour colonnes numériques
        numeric_stats = {}
        for col in analysis['numeric_columns']:
            numeric_stats[col] = {
                'count': df[col].count(),
                'mean': df[col].mean(),
                'std': df[col].std(),
                'var': df[col].var(),
                'min': df[col].min(),
                'max': df[col].max(),
                'median': df[col].median(),
                'skew': df[col].skew(),
                'kurtosis': df[col].kurtosis(),
                'q1': df[col].quantile(0.25),
                'q3': df[col].quantile(0.75),
                'iqr': df[col].quantile(0.75) - df[col].quantile(0.25),
            }
        
        # Analyse bivariée approfondie
        bivariate = {}
        numeric_cols = analysis['numeric_columns']
        categorical_cols = analysis['categorical_columns']
        
        if len(numeric_cols) >= 2:
            # Corrélations et covariances
            corr_matrix = df[numeric_cols].corr()
            cov_matrix = df[numeric_cols].cov()
            
            # Trouver les corrélations les plus fortes
            correlations = []
            for i in range(len(numeric_cols)):
                for j in range(i+1, len(numeric_cols)):
                    correlations.append({
                        'variables': f"{numeric_cols[i]} vs {numeric_cols[j]}",
                        'correlation': corr_matrix.iloc[i,j].round(3)
                    })
            
            correlations.sort(key=lambda x: abs(x['correlation']), reverse=True)
            
            bivariate.update({
                'correlation': corr_matrix.round(2).to_html(classes='table table-striped'),
                'covariance': cov_matrix.round(2).to_html(classes='table table-striped'),
                'top_correlations': correlations[:5]
            })
        
        # Génération des visualisations
        plots = []
        
        # Style configuration
        plt.style.use('default')
        sns.set_theme()
        
        # Distribution plots pour variables numériques
        for col in numeric_cols:
            fig = plt.figure(figsize=(10, 6))
            sns.histplot(data=df, x=col, kde=True)
            plt.title(f'Distribution de {col}')
            plt.tight_layout()
            
            buffer = BytesIO()
            plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight') #Un objet de type BytesIO où le graphique est enregistré. Cela permet de travailler avec l'image en mémoire sans écrire un fichier sur le disque.
            plt.close(fig)
            
            plots.append({
                'title': f'Distribution de {col}',
                'image': base64.b64encode(buffer.getvalue()).decode()
            })

        # Visualisations bivariées
        if len(numeric_cols) >= 2:
            # Heatmap des corrélations
            fig = plt.figure(figsize=(12, 8))
            sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0, fmt='.2f')
            plt.title('Matrice de corrélation')
            plt.tight_layout()
            
            buffer = BytesIO()
            plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
            plt.close(fig)
            
            plots.append({
                'title': 'Heatmap des corrélations',
                'image': base64.b64encode(buffer.getvalue()).decode()
            })

            # Pairplot sélectif
            if len(numeric_cols) > 5:
                # Sélectionner les 5 variables avec les corrélations les plus fortes
                top_corr_vars = set()
                for corr in correlations[:3]:
                    vars_pair = corr['variables'].split(' vs ')
                    top_corr_vars.update(vars_pair)
                selected_cols = list(top_corr_vars)[:5]
            else:
                selected_cols = numeric_cols

            pairplot = sns.pairplot(df[selected_cols])
            buffer = BytesIO()
            pairplot.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
            plt.close(pairplot.fig)
            
            plots.append({
                'title': 'Pairplot des variables les plus corrélées',
                'image': base64.b64encode(buffer.getvalue()).decode()
            })

        # Visualisation des valeurs manquantes
        if analysis['total_missing'] > 0:
            fig = plt.figure(figsize=(12, 6))
            missing_data = df.isnull().sum()
            missing_data = missing_data[missing_data > 0]
            missing_data.plot(kind='bar')
            plt.title('Valeurs manquantes par colonne')
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            buffer = BytesIO()
            plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
            plt.close(fig)
            
            plots.append({
                'title': 'Distribution des valeurs manquantes',
                'image': base64.b64encode(buffer.getvalue()).decode()
            })

        context = {
            'analysis': analysis,
            'value_counts': value_counts,
            'numeric_stats': numeric_stats,
            'bivariate': bivariate,
            'plots': plots
        }
        
        return render(request, 'analysis.html', context)
        
    except Exception as e:
        return render(request, 'upload.html', {'error': f'Erreur lors de l\'analyse: {str(e)}'})