import numpy
import math

def points_for_vine(starting_point):
	results = []
	delta = numpy.array([0,0,-0.08])
	for pixel in range(34):
		results += [starting_point + (pixel * delta)]
	return results

def points_for_tree(center_point, inner_radius, vine_distance):
	all_points = []
	for branch in range(8):
		angle = branch * 2 * math.pi / 8
		direction = numpy.array([math.cos(angle), math.sin(angle), 0])

		for vine in range(5):
			vine_origin = center_point + (direction * (inner_radius + (vine * vine_distance)))
			all_points += points_for_vine(vine_origin)
	
	return all_points


tree_center = numpy.array([0, 0, 3])
points = points_for_tree(tree_center, 0.6, 0.3)
output = ['{{"point":[{0},{1},{2}]}}'.format(x,y,z) for x,y,z in points]
output = ",\n".join(output)
output = "[\n" + output + "\n]\n"

f = file("willow_tree.json", "w+")
f.write(output)
f.close()
