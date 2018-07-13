def str2num(arr):
	nums = []
	for s in arr:
		nums.append(float(s))
	return nums


def read_gq(file):
	weights, points = [], []
	with open(file, 'r') as gq:
		for line in gq:
			w, x = str2num(line.split()[1:])
			weights.append(w)
			points.append(x)
	return weights, points

print(read_gq('data/gq31.txt'))