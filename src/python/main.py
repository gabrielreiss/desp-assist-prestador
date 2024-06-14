# %%
import pandas as pd
import os
import seaborn as sns
import matplotlib.ticker as mtick

BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
DATA_DIR = os.path.join(BASE_DIR, 'data')

# %%
produtos = pd.read_excel(os.path.join(DATA_DIR, 'produtos.xlsx'))

# %%
def convert_data(df):
    df['Data'] = pd.to_datetime(df['Data'])
    df['Data'] = df['Data'].dt.strftime("%Y-%m")
    return df

# %%
def import_dados(excel:list) -> pd.DataFrame:
    resultado = pd.DataFrame()
    for dados in excel:
        df = pd.read_excel(os.path.join(DATA_DIR, dados), sheet_name="movto_balancete_wcp")
        df = df[["Data", "Debito", "Fornecedor"]]
        df = convert_data(df)
        df = df.groupby(by=["Fornecedor", "Data"], as_index=False)["Debito"].agg(
                                soma='sum',
                                media='mean',
                                mediana='median',
                                desvio_padrao='std',
                                minimo='min',
                                maximo='max',
                            ).round(2).sort_values(by=["Data", "soma"], ascending=[True, False])
        df["Conta"] = str(dados).split('.')[0]
        resultado = pd.concat([resultado, df], axis=0, ignore_index=True)
    return resultado

#%%
df = import_dados(['conta 44751 IF pos.xlsx',
                   'conta 40019 Adessao pre.xlsx',
                   'Conta 44752 adesao pos.xlsx',
                   'conta 44753 empresarial pos.xlsx'])

# %%
top5_fornecedores = df.groupby(by=["Fornecedor"], as_index=False)["soma"].sum().sort_values(by=['soma'], ascending=False).head(5)["Fornecedor"].tolist()
top5_df = df.loc[df['Fornecedor'].isin(top5_fornecedores)]
top5_df['Fornecedor'] = top5_df['Fornecedor'].str.split('-', expand=True)[0]
top5_df_geral = top5_df[["Fornecedor","Data","soma"]].groupby(by=["Fornecedor", "Data"], as_index=False)["soma"].agg(
                                soma='sum'
                              ).round(2).sort_values(by=["Data", "soma"], ascending=[True, False])


#%%
print("Análise de Despesas Assistenciais por Prestador de Serviços")
sns.set_theme(style="dark")

def millions_formatter(x, pos):
    """Formats a number to millions with appropriate rounding."""
    if x == 0:
        return 'R$0M'  # Handle zero values specially
    elif x < 1e6:  # For values less than 1 million, show thousands
        return f'R${x:,.0f}K'
    else:  # For values 1 million or above, show millions
        return f'R${x/1e6:,.0f}M'

# Create a formatter object
formatter = mtick.FuncFormatter(millions_formatter)

g = sns.relplot(
    data=top5_df_geral,
    x="Data", y="soma", col="Fornecedor", hue="Fornecedor",
    kind="line", palette="crest", linewidth=4, zorder=5,
    col_wrap=1, height=2, aspect=8, legend=False
)

for conta, ax in g.axes_dict.items():

    # Add the title as an annotation within the plot
    ax.text(.0, .85, conta, transform=ax.transAxes, fontweight="bold", fontsize=12)

    # Plot every year's time series in the background
    sns.lineplot(
        data=top5_df_geral, x="Data", y="soma", units="Fornecedor",
        estimator=None, color=".7", linewidth=1, ax=ax
    )

ax.set_xticks(ax.get_xticks()[::2])
ax.yaxis.set_major_formatter(formatter)

g.set_titles("")
g.set_axis_labels("", "Soma")
g.tight_layout()

g.figure.savefig(os.path.join(BASE_DIR, "output.png"))

# %%
top5_df_geral.to_csv(os.path.join(BASE_DIR, "resultado.csv"), encoding='latin-1', sep=";")
# %%
