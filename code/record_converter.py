import sys
import csv
import json

import feature_extractor

def load_path(fname):
	path_ls = []
	timestamps = []
	action_history = []
	annotations = []
	feedbacks = []
	durations = []
	rows = []

	with open(fname, 'r') as csvfile:
		spamreader = csv.reader(csvfile, delimiter=',', quotechar='"')
		for row in spamreader:
			pstring = row[19]
			if len(pstring) > 10:
				rows.append(row)
				print row[3]
				if row[15] == "":
					timestamps.append([])
				else:
					timestamps.append(\
						map(lambda x: int(x), row[15].split(',')))
				action_history.append(json.loads(row[19]))
				if row[18] == "":
					annotations.append({})
				else:
					annotations.append(json.loads(row[18]))
				feedbacks.append(row[8])
				durations.append([row[10], row[11]])

	return [timestamps, action_history, annotations, \
		feedbacks, durations, rows]

def convert_paths(actions, tstamps):
	new_actions = []
	for act in actions:
		if act[1] != "stroke":
			new_actions.append(act)
		else:
			stroke = json.loads(act[2])
			path = stroke["path"]
			new_act = [tstamps[0], act[1], stroke]
			new_act.append(tstamps[:len(path.split("L"))])
			tstamps = tstamps[len(path.split("L")):]
			new_actions.append(new_act)

	if len(tstamps) != 0:
		return []

	return new_actions

csv.field_size_limit(sys.maxsize)

[timestamps, action_history, annotations, feedbacks, durations, rows] = \
	load_path(sys.argv[1])

records = []
valid_rows = []
for i in range(len(action_history)):
	print i
	record = {}
	actions = convert_paths(action_history[i], timestamps[i])
	if len(actions) == 0:
		print "Reply " + str(i) + " corrupted."
		continue
	record["actions"] = actions
	record["strokes"] = annotations[i]
	record["feedback"] = feedbacks[i]
	record["duration"] = durations[i]
	records.append(record)

	valid_rows.append(rows[i])

	if len(records) == 60:
		break

print "Successfully converted " + str(len(records)) + " replays."

with open((sys.argv[1].split(".")[0] + "_records.txt").format(i), 'w') as f:
	f.write(json.dumps(records))

feature_extractor.extract_features(valid_rows, sys.argv[2])
