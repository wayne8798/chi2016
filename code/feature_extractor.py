import sys
import csv
import json
import string
import math
from PIL import Image

DEBUG_FLAG = True

imageWidth = 0
imageHeight = 0

def load_path(fname):
	path_ls = []
	hist_ls = []
	js_feature_ls = []
	timestamps = []

	with open(fname, 'r') as csvfile:
		spamreader = csv.reader(csvfile, delimiter=',', quotechar='"')
		count = 1
		for row in spamreader:
			if row[0] == "HitId":
				continue

			if DEBUG_FLAG:
				print "Entry #" + str(count)
				print "HitID: " + row[0]
				print "HitTitle: " + row[1]
				print "Annotation: " + row[2]
				print "AssignmentID: " + row[3]
				print "WorkerID: " + row[4]
				print "Status: " + row[5]
				print "AcceptTime: " + row[6]
				print "SubmitTime: " + row[7]
				print "Feedback: " + row[8]
				print "WorkerID: " + row[9]
				print "Prepare Time: " + row[10]
				print "Task Time: " + row[11]
				print "Number of Ops: " + row[12]
				print "Number of Pause: " + row[13]
				print "Number of Del: " + row[14]
				print "Number of Timestamps: " + \
					str(len(row[15].split(",")))
				print "Image width: " + row[16]
				print "Image Height: " + row[17]
				if len(row[18]) > 50:
					print "Path: " + row[18][0:50] + "..."
				else:
					print "Path: " + row[18]
				if len(row[19]) > 50:
					print "History: " + row[19][0:50] + "..."
				else:
					print "History: " + row[19]

				print ""

				count += 1

			if row[18] == "":
				path = {}
			else:
				path = json.loads(row[18])
			path_ls.append(path)

			hist_ls.append(json.loads(row[19]))

			js_feature_ls.append([int(row[10]), int(row[11]), \
				int(row[12]), int(row[13]), int(row[14]), row[8]])

			if row[15] == "":
				timestamps.append([])
			else:
				timestamps.append( \
					map(lambda x: int(x), row[15].split(',')))

			global imageWidth
			global imageHeight

			imageWidth = int(row[16])
			imageHeight = int(row[17])

	return [path_ls, timestamps, hist_ls, js_feature_ls]

def load_path_by_row(rows):
	path_ls = []
	hist_ls = []
	js_feature_ls = []
	timestamps = []

	count = 1
	for row in rows:
		if DEBUG_FLAG:
			print "Entry #" + str(count)
			print "HitID: " + row[0]
			print "HitTitle: " + row[1]
			print "Annotation: " + row[2]
			print "AssignmentID: " + row[3]
			print "WorkerID: " + row[4]
			print "Status: " + row[5]
			print "AcceptTime: " + row[6]
			print "SubmitTime: " + row[7]
			print "Feedback: " + row[8]
			print "WorkerID: " + row[9]
			print "Prepare Time: " + row[10]
			print "Task Time: " + row[11]
			print "Number of Ops: " + row[12]
			print "Number of Pause: " + row[13]
			print "Number of Del: " + row[14]
			print "Number of Timestamps: " + \
				str(len(row[15].split(",")))
			print "Image width: " + row[16]
			print "Image Height: " + row[17]
			if len(row[18]) > 50:
				print "Path: " + row[18][0:50] + "..."
			else:
				print "Path: " + row[18]
			if len(row[19]) > 50:
				print "History: " + row[19][0:50] + "..."
			else:
				print "History: " + row[19]

			print ""

			count += 1

		if row[18] == "":
			path = {}
		else:
			path = json.loads(row[18])
		path_ls.append(path)

		hist_ls.append(json.loads(row[19]))

		js_feature_ls.append([int(row[10]), int(row[11]), \
			int(row[12]), int(row[13]), int(row[14]), row[8]])

		if row[15] == "":
			timestamps.append([])
		else:
			timestamps.append( \
				map(lambda x: int(x), row[15].split(',')))

		global imageWidth
		global imageHeight

		imageWidth = int(row[16])
		imageHeight = int(row[17])

	return [path_ls, timestamps, hist_ls, js_feature_ls]

def calc_angle(p1, p2, p3):
	a = [p1[0] - p2[0], p1[1] - p2[1]]
	b = [p1[0] - p3[0], p1[1] - p3[1]]

	division = (a[0] * b[0] + a[1] * b[1]) / \
		(calc_seg_length(p1, p2) * calc_seg_length(p1, p3))

	assert division < 1.01 and division > -1.01
	if division > 1:
		division = 1
	elif division < -1:
		division = -1

	angle = math.acos(division)
	return angle

def calc_curvature(path):
	angle_ls = []
	for s in path:
		angles = []

		if len(s) < 3:
			angles = [0]
			continue

		pprev_p = s[0]
		prev_p = s[1]
		for p in s[2:]:
			p12 = calc_seg_length(pprev_p, prev_p)
			p13 = calc_seg_length(pprev_p, p)
			p23 = calc_seg_length(prev_p, p)

			angles.append(math.pi - calc_angle(prev_p, pprev_p, p))

			pprev_p = prev_p
			prev_p = p

		angle_ls.append(angles)

	return angle_ls

def calc_seg_length(p1, p2):
	x = p1[0] - p2[0]
	y = p1[1] - p2[1]
	return math.sqrt(x*x + y*y)

def calc_length(path):
	length_ls = []
	for s in path:
		length = []
		prev_p = s[0]
		for p in s[1:]:
			length.append(calc_seg_length(prev_p, p))
			prev_p = p
		length_ls.append(length)

	return length_ls

def calc_average_seg_size(length_ls):
	seg_count = 0
	length_sum = 0
	for s in length_ls:
		for l in s:
			length_sum += l
			seg_count += 1
	return length_sum / seg_count

def find_max_seg_size(length_ls):
	max_l = 0
	for s in length_ls:
		for l in s:
			if l > max_l:
				max_l = l
	return max_l

def calc_speed(length_ls, timestamp):
	all_tstamps = timestamp
	speed_ls = []
	accel_ls = []

	for ls in length_ls:
		tstamps = all_tstamps[:len(ls)+1]
		all_tstamps = all_tstamps[len(ls)+1:]

		duration_ls = []
		prev_t = tstamps[0]
		for t in tstamps[1:]:
			duration_ls.append(t - prev_t)
			prev_t = t

		# smoothing
		smooth_length_ls = []
		smooth_duration_ls = []
		length_sum = 0
		duration_sum = 0

		for i in range(len(ls)):
			length_sum += ls[i]
			duration_sum += duration_ls[i]

			if duration_sum > 50 or i == (len(ls) - 1):
				smooth_length_ls.append(length_sum)
				smooth_duration_ls.append(duration_sum)

				length_sum = 0
				duration_sum = 0

		for i in range(len(smooth_length_ls)):
			if smooth_duration_ls[i] != 0:
				speed_ls.append(\
					1000 * smooth_length_ls[i]/smooth_duration_ls[i])
			else:
				speed_ls.append(0)

		s1 = smooth_length_ls[0]
		t1 = smooth_duration_ls[0]

		for i in range(1, len(smooth_length_ls)):
			s2 = smooth_length_ls[i]
			t2 = smooth_duration_ls[i]

			v1 = 1000 * s1/t1
			v2 = 1000 * s2/t2

			accel_ls.append(abs(2000 * (v2 - v1) / (t1 + t2)))

			s1 = s2
			t1 = t2

	return [speed_ls, accel_ls]

def calc_smooth_path(path):
	s_path = []
	for s in path:
		s_s = [s[0]]
		prev_p = s[0]
		for p in s[1:]:
			if calc_seg_length(prev_p, p) >= 5:
				s_s.append(p)
				prev_p = p
		if calc_seg_length(prev_p, s[-1]) > 0:
			s_s.append(s[-1])
		s_path.append(s_s)
	return s_path

def mark_pixels(p1, p2, stroke_width, bitmap):
	left_x = int(p1[0]) if p1[0] < p2[0] else int(p2[0])
	left_x -= stroke_width/2
	left_x = 0 if left_x < 0 else left_x

	right_x = int(math.ceil(p1[0])) if p1[0] > p2[0] else int(math.ceil(p2[0]))
	right_x += stroke_width/2
	right_x = (len(bitmap[0]) - 1) if right_x > (len(bitmap[0]) - 1) else right_x

	down_y = int(p1[1]) if p1[1] < p2[1] else int(p2[1])
	down_y -= stroke_width/2
	down_y = 0 if down_y < 0 else down_y

	up_y = int(math.ceil(p1[1])) if p1[1] > p2[1] else int(math.ceil(p2[1]))
	up_y += stroke_width/2
	up_y = (len(bitmap) - 1) if up_y > (len(bitmap) - 1) else up_y

 	for y in range(down_y, up_y + 1):
		for x in range(left_x, right_x + 1):
			p = [x,y]
			if calc_seg_length(p, p1) <= stroke_width/2 or \
				calc_seg_length(p, p2) <= stroke_width/2:
				bitmap[y][x] = 1
			elif (calc_angle(p1, p, p2) <= math.pi/2) and \
				(calc_angle(p2, p, p1) <= math.pi/2):
				a = calc_seg_length(p, p1)
				b = calc_seg_length(p, p2)
				c = calc_seg_length(p1, p2)
				area = (a+b+c)*(b+c-a)*(c+a-b)*(a+b-c)
				if area <= 0:
					h = 0
				else:
					h = math.sqrt(area)/(2*c)
				if h <= stroke_width/2:
					bitmap[y][x] = 1

def save_image(bitmap, fname):
	x = len(bitmap[0])
	y = len(bitmap)
	img = Image.new('RGB', (x, y), 'white')
	pixels = img.load()

	for i in range(img.size[0]):
		for j in range(img.size[1]):
			if bitmap[j][i] > 0:
				pixels[i,j] = (100,100,100)

	img.save(fname + '.jpeg', 'JPEG')

def create_bitmap(path, stroke_width, count):
	max_x = 0
	max_y = 0
	for s in path:
		for seg in s:
			x_ceil = int(math.ceil(seg[0]))
			y_ceil = int(math.ceil(seg[1]))
			if x_ceil > max_x:
				max_x = x_ceil
			if y_ceil > max_y:
				max_y = y_ceil

		max_x += stroke_width/2
		max_y += stroke_width/2

	bitmaps = []
	for s in path:
		bitmap = [[0 for i in range(max_x + 1)] \
			for j in range(max_y + 1)]

		prev_p = s[0]
		for p in s[1:]:
			if calc_seg_length(prev_p, p) == 0:
				continue
			mark_pixels(prev_p, p, stroke_width, bitmap)
			prev_p = p

		bitmaps.append(bitmap)

	bitmap = [[0 for i in range(max_x + 1)] \
		for j in range(max_y + 1)]
	for b in bitmaps:
		for j in range(max_y + 1):
			for i in range(max_x + 1):
				bitmap[j][i] += b[j][i]

	# for test purpose, save bitmap to a file
	# save_image(bitmap, 'test' + str(count))

	return bitmap

def find_max(ls):
	max_val = 0
	for l in ls:
		if len(l) == 0:
			continue
		if max(l) > max_val:
			max_val = max(l)
	return max_val

def find_min(ls):
	min_val = 0
	for l in ls:
		if len(l) == 0:
			continue
		if min(l) > min_val:
			min_val = min(l)
	return min_val	

def preprocess_path(p, timestamp, count):
	feature_vec = []

	# parse raw path string
	path = []
	stroke_colors = []
	seg_count = 0
	max_stroke_width = 0
	for s in p:
		stroke = s['path']
		if len(stroke) == 0:
			continue

		stroke_color = s['stroke']
		if not stroke_color in stroke_colors:
			stroke_colors.append(stroke_color)
		
		stroke_width = int(s['stroke-width'])
		if stroke_width > max_stroke_width:
			max_stroke_width = stroke_width

		stroke_segs = map(lambda p : [float(p[0]), float(p[1])], \
			map(lambda s : s.split(','), stroke[1:].split('L')))
		path.append(stroke_segs)
		seg_count += len(stroke_segs) - 1

	stroke_count = len(path)
	feature_vec.append(stroke_count)

	feature_vec.append(len(stroke_colors))

	# calculate bounding box size
	left_x = 10000
	right_x = 0
	down_y = 10000
	up_y = 0
	for s in path:
		for p in s:
			x = p[0]
			y = p[1]
			if x < left_x:
				left_x = x
			if x > right_x:
				right_x = x
			if y < down_y:
				down_y = y
			if y > up_y:
				up_y = y
	bounding_box_area = int((right_x - left_x) * (up_y - down_y)) \
		if right_x else 0

	feature_vec.append(bounding_box_area)
	feature_vec.append(bounding_box_area / (float)(imageHeight * imageWidth))
	# if bounding_box_area < 50000:
	#	feature_vec.append(bounding_box_area / 10000)
	# else:
	#	feature_vec.append(bounding_box_area / 50000 + 4)

	# calculate length data

	length_ls = calc_length(path)
	# feature_vec.append(calc_average_seg_size(length_ls))
	# feature_vec.append(find_max_seg_size(length_ls))

	# speed & acceleration
	[speed_ls, accel_ls] = \
		calc_speed(length_ls, timestamp[-(seg_count+stroke_count):])

	feature_vec.append(\
		sum(speed_ls)/len(speed_ls) if len(speed_ls) else 0)
	feature_vec.append(max(speed_ls) if len(speed_ls) else 0)

	feature_vec.append(\
		sum(accel_ls)/len(accel_ls) if len(accel_ls) else 0)
	feature_vec.append(max(accel_ls) if len(accel_ls) else 0)

	# calculate smoothed path
	# smooth_path = calc_smooth_path(path)

	# calculate angles
	# angle_ls = calc_curvature(smooth_path)
	# feature_vec.append(int(find_max(angle_ls)))
	# feature_vec.append(find_max(angle_ls))
	# feature_vec.append(find_min(angle_ls))

	# create bitmap
	bitmap = create_bitmap(path, max_stroke_width, count)

	covered_pixel_count = 0
	overpaint_pixel_count = 0
	for i in range(len(bitmap)):
		for j in range(len(bitmap[0])):
			if bitmap[i][j] > 0:
				covered_pixel_count += 1
			if bitmap[i][j] > 1:
				overpaint_pixel_count += 1

	feature_vec.append(covered_pixel_count)
	feature_vec.append(overpaint_pixel_count)

	# if overpaint_pixel_count < 3000:
	#	feature_vec.append(overpaint_pixel_count / 500)
	# else:
	#	feature_vec.append(6)

	return feature_vec

def export_arff(features, labels):
	fout = open('paint.arff', 'w')
	fout.write("@relation paint\n\n")

	fout.write("@attribute stroke_count numeric\n")
	fout.write("@attribute stroke_color_count numeric\n")
	# fout.write("@attribute seg_count numeric\n")
	# fout.write("@attribute avg_stroke_width numeric\n")
	# fout.write("@attribute max_stroke_width numeric\n")
	fout.write("@attribute bounding_box_area numeric\n")
	fout.write("@attribute bounding_box_percent numeric\n")
	fout.write("@attribute avg_speed numeric\n")
	fout.write("@attribute max_speed numeric\n")
	fout.write("@attribute avg_accel numeric\n")
	fout.write("@attribute max_accel numeric\n")
	# fout.write("@attribute max_angle numeric\n")
	# fout.write("@attribute min_angle numeric\n")
	fout.write("@attribute covered_area numeric\n")
	fout.write("@attribute overpaint_count numeric\n")
	fout.write("@attribute prepare_time numeric\n")
	fout.write("@attribute task_time numeric\n")
	fout.write("@attribute ops_count numeric\n")
	fout.write("@attribute pause_count numeric\n")
	fout.write("@attribute del_count numeric\n")
	fout.write("@attribute feedback_char_count numeric\n")
	fout.write("@attribute feedback_word_count numeric\n")
	fout.write("@attribute avg_word_length numeric\n")
	fout.write("@attribute longest_word numeric\n")
	fout.write("@attribute response_time numeric\n")
	fout.write("@attribute review_time numeric\n")
	fout.write("@attribute undo_count numeric\n")
	fout.write("@attribute typing_speed numeric\n")
	fout.write("@attribute insert_count numeric\n")
	fout.write("@attribute text_ratio numeric\n")

	# fout.write("@attribute feedback_length numeric\n\n@data\n")

	fout.write("@attribute class {good, bad}\n\n@data\n")
	# fout.write("@attribute class {1.0,2.0,3.0,4.0,5.0}\n\n@data\n")

	for i in range(len(features)):
		fout.write(",".join(str(x) for x in features[i]) + ",")
		if labels[i] == 1:
			fout.write("good\n")
		else:
			fout.write("bad\n")
		# fout.write(str(labels[i]) + "\n")
	fout.close()

def process_history_features(history):
	new_features = []
	for h in history:
		vec = []

		start_time = 0
		first_act_time = 0				
		text_history = []
		undo_count = 0
		for act in h:
			if start_time != 0 and first_act_time == 0:
				first_act_time = act[0]
			if act[1] == "start":
				start_time = act[0]
			if act[1] == "text_update":
				text_history.append(act)
			if act[1] == "undo":
				undo_count += 1

		response_time = first_act_time - start_time
		task_time = h[-1][0] - start_time
		review_time = h[-1][0] - h[-2][0]

		vec.append(response_time)
		vec.append(review_time)
		vec.append(undo_count)

		if len(text_history) > 1:
			typing_count = 0
			duration_sum = 0
			insert_count = 0
			prev_act = text_history[0]
			for act in text_history[1:]:
				if len(act[2]) - len(prev_act[2]) == 1:
					typing_count += 1
					duration_sum += act[0] - prev_act[0]
					if act[2][:-1] != prev_act[2]:
						insert_count += 1
				prev_act = act
			if typing_count > 0:
				vec.append(float(duration_sum)/typing_count)
			else:
				vec.append(1000000.0)
			vec.append(insert_count)
			vec.append(float(duration_sum)/task_time)
		else:
			vec.append(10000)
			vec.append(0)
			vec.append(0)

		new_features.append(vec)
	return new_features

def process_js_features(js_features):
	new_features = []
	for v in js_features:
		vec = []
		prepare_time = v[0]
		vec.append(prepare_time)
		
		task_time = v[1]
		vec.append(task_time)

		ops_count = v[2]
		vec.append(ops_count)

		pause_count = v[3]
		vec.append(pause_count)

		del_count = v[4]
		vec.append(del_count)

		feedback = v[5]
		vec.append(len(feedback))
		vec.append(len(feedback.split()))

		word_count = 0
		longest_word = 0
		length_sum = 0
		for w in feedback.split():
			if len(w) > 0:
				word_count += 1.0
				length_sum += len(w)
				if len(w) > longest_word:
					longest_word = len(w)

		vec.append(length_sum/word_count \
			if word_count else 0)
		vec.append(longest_word)

		new_features.append(vec)
	return new_features

def extract_features(rows, flabel):
	[paths, timestamps, history, js_features] = load_path_by_row(rows)

	hist_features = process_history_features(history)
	js_features = process_js_features(js_features)

	count = 0
	feature_vec_ls = []

	for p in paths:
		if count % 10 == 0:
			print count

		feature_vec_ls.append(preprocess_path(p, timestamps[count], count) \
			+ js_features[count] + hist_features[count])
		count += 1

	labels = []
	with open(flabel, "r") as f:
		line = f.readline()
		while line != "":
			if float(line[:-1]) >= 3:
				labels.append(1)
			else:
				labels.append(0)
			# labels.append(round(float(line[:-1])))
			line = f.readline()

	export_arff(feature_vec_ls, labels)
