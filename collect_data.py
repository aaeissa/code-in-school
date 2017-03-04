# TODO
# get rid of pdf/txt/file_path vars, use format{} where appropriate

from requests import get
import textract
import csv
import re


def get_csv_data(file):
	with open(file, 'r') as f:
		csv_data = []
		reader = csv.reader(f)
		for row in reader:
			csv_data.append(row)

		cleaned_csv = []
		for i in range(len(csv_data)):
			cleaned_csv.append(strip_num(csv_data[i][0]))
		return cleaned_csv


def strip_num(str_total):
	num_total = ''
	for c in str_total:
		if c != ',':
			num_total += c
	num_total = int(num_total)
	return num_total


def find_data(regex, cleaned_data):
	data = re.compile(regex)
	data = data.findall(cleaned_data)
	return data


def minority_data(race, cleaned_data):
	regex = r'(?:only|no) \d?\d?,?\d?\d?\d? students?(?:\s)?(?:was|were) {}'.format(race)
	data = re.compile(regex)
	data = data.findall(cleaned_data)

	if len(data) > 0:
		data = data[0].split()
		students = int(strip_num(data[1]))
		return students
	else:
		students = 0
		return students

states = ['AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'DC', 'FL', 'GA', 'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD', 'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ', 'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY']

base_url = 'https://code.org/advocacy/state-facts/'
pdf = '.pdf'
txt = '.txt'
file_path = 'data/'
cols = ['State', 'Population', 'Median_Income', 'Total_Schools', 'Total_AP', 'Female_AP', 'Hispanic/Latino_AP', 'Black_AP', 'Nat_Am_AP', 'Nat_Haw_AP']

# Source: http://www.census.gov/data/tables/2016/demo/popest/state-total.html
population = get_csv_data('data_sets/statePopulation.csv')

# Source: https://www.census.gov/content/dam/Census/library/publications/2016/demo/acsbr15-02.pdf
income = get_csv_data('data_sets/stateIncome.csv')

csv_count = 0

with open('stateData.csv', 'a') as f:
	writer = csv.writer(f)
	writer.writerow(cols)

	for state in states:
		print('testing '+state)
		# all state info stores in this lis, for csv row
		state_data = [state, population[csv_count], income[csv_count]]

		r = get(base_url+state+pdf)

		# download fact sheet to /data
		with open(file_path+state+pdf, 'wb') as f:
			f.write(r.content)

		# extract text from PDF fact sheets
		text = textract.process(file_path+state+pdf, method='pdfminer')

		# text is littered with tabs and newlines
		cleaned_data = ''
		for c in text:
			if c != '\t' and c != '\n':
				cleaned_data += c
			elif c == '\t':
				cleaned_data += ' '

		# write the cleaned text to a .txt file for each state
		with open(file_path+state+txt, 'wb') as f:
			f.write(cleaned_data)

		# Number of high schools with AP CS classes
		print('testing schools')
		regex = r'Only \d?\d?\d? schools in '+state
		data = find_data(regex, cleaned_data)
		try:
			schools = data[0].split(' ')
			state_data.append(int(schools[1]))
		except:
			print('No schools offering AP course in {}'.format(state))

		# Total number of students that took the AP exam
		print('testing totalAP')
		regex = r'Only \d?\d?,?\d?\d?\d? high school students'
		data = find_data(regex, cleaned_data)
		total = data[0].split()
		total = strip_num(total[1])
		state_data.append(total)

		# Number of female students that took the AP exam
		print('testing womenAP')
		regex = r'(?:\d?\d?\d?%were|\d?\d?\d?% were)'
		data = find_data(regex, cleaned_data)

		if len(data) > 1:
			women = data[1].split('%')
			women = int((strip_num(women[0]) * .01) * total)
			state_data.append(int(women))
		else:
			women = 0
			state_data.append(women)

		races = ['Hispanic', 'Black', '(?:Native American|NativeAmerican)', '(?:Native Hawaiian|NativeHawaiian)']

		for dem in races:
			state_data.append(minority_data(dem, cleaned_data))

		writer.writerow(state_data)
		csv_count += 1