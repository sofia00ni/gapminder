import streamlit as st
import pandas as pd
import plotly.express as px

st.write("BIPM Project - Unlocking Lifetimes: Visualizing Progress in Longevity and Poverty Eradication ")


pop = pd.read_csv('pop.csv')
lex = pd.read_csv('lex.csv')
gni = pd.read_csv('ny_gnp_pcap_pp_cd.csv')

for year in gni.columns[1:]:
    gni[year] = (
        gni[year]
        .str.replace(',', '', regex=False)
        .str.replace('k', '', regex=False)
        .str.strip()
        .replace('', '0')
    )
    gni[year] = pd.to_numeric(gni[year], errors='coerce').fillna(0) * 1000

pop_long = pop.melt(id_vars=['country'], var_name='year', value_name='population')
lex_long = lex.melt(id_vars=['country'], var_name='year', value_name='life_expectancy')
gni_long = gni.melt(id_vars=['country'], var_name='year', value_name='gni_per_capita')

pop_long['year'] = pop_long['year'].astype(int)
lex_long['year'] = lex_long['year'].astype(int)
gni_long['year'] = gni_long['year'].astype(int)

pop_long['population'] = pd.to_numeric(pop_long['population'], errors='coerce').fillna(0)
lex_long['life_expectancy'] = pd.to_numeric(lex_long['life_expectancy'], errors='coerce').fillna(0)
gni_long['gni_per_capita'] = pd.to_numeric(gni_long['gni_per_capita'], errors='coerce').fillna(0)

df = pop_long.merge(lex_long, on=['country', 'year']).merge(gni_long, on=['country', 'year'])

st.title("World Development Indicators")

min_year = df['year'].min()
max_year = df['year'].max()
selected_year = st.slider('Select Year', min_year, max_year, min_year, step=1)

available_countries = sorted(df['country'].unique())
default_countries = ['United States', 'Germany']
default_countries = [c for c in default_countries if c in available_countries]
selected_countries = st.multiselect('Select Countries', options=available_countries, default=default_countries)

filtered_df = df[(df['year'] == selected_year) & (df['country'].isin(selected_countries))]

# Debug-Infos
st.write(f"Data points for year {selected_year} and countries {selected_countries}: {len(filtered_df)}")
st.write(filtered_df[['population', 'gni_per_capita', 'life_expectancy']].describe())

if len(filtered_df) == 0:
    st.warning("No data available for this selection.")
else:
    fig = px.scatter(
        filtered_df,
        x='gni_per_capita',
        y='life_expectancy',
        size=filtered_df['population'] / 1_000_000 + 1,  # Skalieren und Minimum 1
        color='country',
        hover_name='country',
        log_x=True,
        size_max=100,
        labels={
            'gni_per_capita': 'GNI per Capita (PPP, USD)',
            'life_expectancy': 'Life Expectancy (years)',
            'population': 'Population',
            'country': 'Country'
        },
        title=f'World Development Indicators in {selected_year}'
    )

    st.plotly_chart(fig, use_container_width=True)
