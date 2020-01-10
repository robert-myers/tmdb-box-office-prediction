from collections import Counter
import numpy as np
from itertools import chain
import pandas as pd
import seaborn as sns
import ast

def count_dict_items(df, dct_columns):
	top_counts = []
	for column in dct_columns:
		top_count = Counter(chain(*df[column].apply(lambda row: [dct["name"]
																													 for dct in row] if row else ["NO DATA"]))).most_common()
		top_counts.append(top_count)
	return pd.DataFrame(top_counts, index=dct_columns).T

def find_in_movie(row, name):
	"""
	input:
		row is a list of dictionaries
		name is a string

	output:
		boolean value
	"""
	for ele in row:
		if ele["name"].lower() == name.lower():
			return True
	return False

def movie_search(df, name, category):
	"""
	input:
		df is a pandas dataframe.
		name is the string to query in the chosen category.
		category is a string of the column name to query.
		categories options include:
			belongs_to_collection
			genres
			production_companies
			production_countries
			spoken_languages
			Keywords
			cast
			crew

	output:
		pandas dataframe with filtered search results
	"""
	return df[df[category].apply(lambda row: find_in_movie(row, name))]

def movie_search_aggregate(df, ele, category, agg="sum"):
	"""
	helper function for box_office_from_search()
	"""
	if agg == "sum":
		budget = float(movie_search(df, ele, category)[["budget"]].sum())
		revenue = float(movie_search(df, ele, category)[["revenue"]].sum())
	elif agg == "mean":
		budget = float(movie_search(df, ele, category)[["budget"]].mean())
		revenue = float(movie_search(df, ele, category)[["revenue"]].mean())
	else:
		return "invalid agg argument"
	return budget, revenue

def box_office_from_search(df, category, data_to_find, agg="sum", top=21):
	"""
	input:
		category is a string of the column name to query.
		categories options include:
			belongs_to_collection
			genres
			production_companies
			production_countries
			spoken_languages
			Keywords
			cast
			crew
		top is an int of how many elements to iterate over in chosen category.
		data_to_find is the where the search terms come from.
		df is the dataframe being searched.

	output:
		names is a list of strings used to search the df.
		budgets is a list of floats.
		revenues is a list of floats.
		nets is a list of revenues minus budgets.
	"""
	names = [name for name, count in data_to_find[category][:top]]
	budgets = []
	revenues = []
	nets = []

	for ele, count in data_to_find[category][:top]:
		budget, revenue = movie_search_aggregate(df, ele, category, agg)
		net = revenue - budget

		budgets.append(budget)
		revenues.append(revenue)
		nets.append(net)

	return names, budgets, revenues, nets

def barplot_movies(df, category, agg, ax, data_to_find, top=21):
	names, budgets, revenues, nets = box_office_from_search(df=df,
		category=category, agg=agg, top=top, data_to_find=data_to_find)
	sns.set_color_codes("colorblind")
	sns.barplot(x=revenues, y=list(range(len(names))), orient="h", ax=ax,
							label=f"{agg.title()} Revenue", color="green", alpha=0.5)
	sns.barplot(x=budgets, y=list(range(len(names))), orient="h", ax=ax,
							label=f"{agg.title()} Budget", color="red", alpha=0.5)
	ax.legend(frameon=True, fontsize="large")
	ax.set_yticklabels(names)

def count_winning_pairs(sample_1, sample_2):
	sample_1, sample_2 = np.array(sample_1), np.array(sample_2)
	n_total_wins = 0
	for x in sample_1:
		n_wins = np.sum(x > sample_2) + 0.5*np.sum(x == sample_2)
		n_total_wins += n_wins
	return n_total_wins

def dataframe_dictionary(df, category, data_to_find):
	dfs = {}
	for ele, _ in data_to_find[category].dropna():
		ele = ele.lower()
		dfs[ele] = movie_search(df, ele, category)
	return dfs
