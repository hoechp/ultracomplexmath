package util.kd.clustering;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Vector;


public class Clustering {

	private HashSet<Vector<Double>> data;
	public HashSet<Vector<Double>> getData() {
		return data;
	}

	public int getDim() {
		return dim;
	}

	private int dim;
	
	public Clustering(HashSet<Vector<Double>> d) {
		data = d;
		dim = 0;
		for (Vector<Double> p: data) {
			dim = p.size();
			break;
		}
	}
	
	public Clustering(int size) {
		data = new HashSet<Vector<Double>>();
		dim = size;
	}
	
	public void addData(Vector<Double> d) {
		if (data == null) {
			data = new HashSet<Vector<Double>>();
		}
		data.add(d);
	}

	/**
	 * nicht-deterministisches dichtebasiertes hierarchisches grid-clustering<p>
	 * 
	 * braucht grid-dimensionen<p>
	 * 
	 * kann selbst (andere) grids in grids abbilden, zusammenhaengende formen,
	 * dichteste bereiche, hierarchien von clustern, usw.
	 */
	public HashSet<HierarchicalCluster> gridClustering(int gridNum) {
		HashMap<Integer, HashSet<Vector<Double>>> gridRaw = makeGrid(gridNum, true);
		HashMap<Integer, HierarchicalCluster> grid = new HashMap<Integer, HierarchicalCluster>();
		for (int i: gridRaw.keySet()) {
			grid.put(i, new HierarchicalCluster(gridRaw.get(i)));
		}
		HashMap<Integer, Integer> area = new HashMap<Integer, Integer>();
		HashMap<Integer, Vector<Integer>> pos = new HashMap<Integer, Vector<Integer>>();
		for (int c: grid.keySet()) {
			// init area
			area.put(c, 1);
			// decode grid position
			Vector<Integer> p = new Vector<Integer>();
			int cCopy = c;
			for (int i = 0; i < dim; ++i) {
				p.add(cCopy % gridNum);
				cCopy /= gridNum;
			}
			pos.put(c, p);
		}
		// find adjacent clusters
		HashMap<Integer, Vector<Integer>> adjacent = new HashMap<Integer, Vector<Integer>>();
		for (int c1: grid.keySet()) {
nextPoint:	for (int c2: grid.keySet()) {
				if (c1 != c2) {
					int diff = 0;
					for (int i = 0; i < dim; ++i) {
						diff += Math.abs(pos.get(c1).get(i) - pos.get(c2).get(i));
						if (diff > 1) {
							continue nextPoint;
						}
					}
					if (diff == 1) {
						if (adjacent.containsKey(c1)) {
							adjacent.get(c1).add(c2);
						} else {
							Vector<Integer> adj = new Vector<Integer>();
							adj.add(c2);
							adjacent.put(c1, adj);
						}
					}
				}
			}
		}
		HashSet<Integer> untouchable = new HashSet<Integer>();
		boolean clusterExists = true;
		while (clusterExists) {
			clusterExists = false;
			// find densest unclustered cluster
			int densest = -1;
			double density = -1; 
			for (int c: grid.keySet()) {
				if (untouchable.contains(c)) {
					continue;
				}
				double density2 = (double)grid.get(c).getDataSet().size() / (double)area.get(c);
				if (density2 > density) {
					density = density2;
					densest = c;
				}
			}
			if (densest != -1) {
				clusterExists = true;
			} else {
				continue;
			}
			int key = -1;
			boolean clusterFound = true;
			while (clusterFound) {
				density = (double)grid.get(densest).getDataSet().size() / (double)area.get(densest);
				clusterFound = false;
				// find densest adjacent cluster with less density
				int densest2 = -1;
				double maxDensity = -1; 
				for (int c: adjacent.get(densest)) {
					double density2 = (double)grid.get(c).getDataSet().size() / (double)area.get(c);
					if (density2 < density) {
						if (density2 > maxDensity) {
							maxDensity = density2;
							densest2 = c;
						}
					}
				}
				if (densest2 != -1) {
					clusterFound = true;
				} else {
					continue;
				}
				// join clusters (merge one into another; update points, area, adjacent clusters, untouchable)
				grid.get(densest).merge(grid.get(densest2));
				grid.get(densest).setKey(++key);
				grid.remove((Integer)densest2); // remove other from grid
				area.put(densest, area.get(densest) + area.get(densest2)); // add area
				// copy links from densest2 to densest
				for (int i: adjacent.get(densest2)) {
					if (i != densest && !adjacent.get(densest).contains(i)) {
						adjacent.get(densest).add(i);
					}
				}
				// update links to densest2 to densest
				for (int i: adjacent.keySet()) {
					for (int k = 0; k < adjacent.get(i).size(); ++k) {
						if (adjacent.get(i).get(k) == densest2) {
							if (i != densest && !adjacent.get(i).contains(densest)) {
								adjacent.get(i).set(k, densest);
							} else {
								adjacent.get(i).remove(k);
							}
						}
					}
				}
			}
			// make this cluster not be considered anymore
			untouchable.add(densest);
			for (int i: adjacent.keySet()) {
				adjacent.get(i).remove((Integer)densest);
			}
		}
		HashSet<HierarchicalCluster> result = new HashSet<HierarchicalCluster>();
		for (int i: untouchable) {
			result.add(grid.get(i));
		}
		return result;
	}

	/**
	 * deterministisches dichtebasiertes grid-clustering<p>
	 * 
	 * braucht grid-dimensionen und dichte-schwellenwert<p>
	 * 
	 * wie dichtebasiertes clustering nur mit bloecken -> kann zusammenhaengende formen abbilden
	 * 
	 * filtert noise
	 */
	public HashSet<Cluster> subspaceClustering(int gridNum, int minP) {
		HashMap<Integer, HashSet<Vector<Double>>> gridRaw = makeGrid(gridNum);
		HashMap<Integer, Cluster> grid = new HashMap<Integer, Cluster>();
		HashMap<Integer, Vector<Integer>> pos = new HashMap<Integer, Vector<Integer>>();
		HashMap<Integer, Boolean> dense = new HashMap<Integer, Boolean>();
		ArrayList<Cluster> denseClusters = new ArrayList<Cluster>();
		for (int i: gridRaw.keySet()) {
			grid.put(i, new HierarchicalCluster(gridRaw.get(i)));
		}
		for (int c: grid.keySet()) {
			// find dense clusters
			if (grid.get(c).getDataSet().size() >= minP) {
				dense.put(c, true);
				denseClusters.add(grid.get(c));
				// decode grid position
				Vector<Integer> p = new Vector<Integer>();
				int cCopy = c;
				for (int i = 0; i < dim; ++i) {
					p.add(cCopy % gridNum);
					cCopy /= gridNum;
				}
				pos.put(c, p);
			} else {
				dense.put(c, false);
			}
		}
		// find adjacent dense clusters
		HashMap<Integer, Vector<Integer>> adjacent = new HashMap<Integer, Vector<Integer>>();
		for (int c1: grid.keySet()) {
			if (dense.get(c1)) {
nextPoint:		for (int c2: grid.keySet()) {
					if (dense.get(c2)) {
						if (c1 != c2) {
							int diff = 0;
							for (int i = 0; i < dim; ++i) {
								diff += Math.abs(pos.get(c1).get(i) - pos.get(c2).get(i));
								if (diff > 1) {
									continue nextPoint;
								}
							}
							if (diff == 1) {
								if (adjacent.containsKey(c1)) {
									adjacent.get(c1).add(c2);
								} else {
									Vector<Integer> adj = new Vector<Integer>();
									adj.add(c2);
									adjacent.put(c1, adj);
								}
							}
						}
					}
				}
			}
		}
		HashSet<Integer> untouchable = new HashSet<Integer>();
		boolean clusterExists = true;
		while (clusterExists) {
			clusterExists = false;
			// find unclustered dense cluster
			int ind1 = -1;
			if (denseClusters.size() > untouchable.size()) {
				for (int i = 0; i < denseClusters.size(); ++i) {
					if (!untouchable.contains(i)) {
						ind1 = i;
						break;
					}
				}
			}
			int toJoin1 = -1;
			if (ind1 != -1) {
				for (int i: grid.keySet()) {
					if (grid.get(i) == denseClusters.get(ind1)) {
						toJoin1 = i;
						break;
					}
				}
				if (toJoin1 == -1) {
					continue;
				}
				clusterExists = true;
			} else {
				continue;
			}
			boolean clusterFound = true;
			while (clusterFound) {
				clusterFound = false;
				// find dense adjacent cluster to join
				int toJoin2 = -1;
				if (adjacent.get(toJoin1) == null) {
					break;
				}
				for (int c: adjacent.get(toJoin1)) {
					toJoin2 = c;
					break;
				}
				int ind2 = -1;
				if (toJoin2 != -1) {
					for (int i = 0; i < denseClusters.size(); ++i) {
						if (denseClusters.get(i) == grid.get(toJoin2)) {
							ind2 = i;
							break;
						}
					}
					if (ind2 == -1) {
						continue;
					}
					clusterFound = true;
				} else {
					continue;
				}
				// join clusters (merge one into another; update points, adjacent clusters, denseClusters)
				denseClusters.get(ind1).merge(denseClusters.get(ind2));
				denseClusters.remove(ind2); // remove other from grid
				// copy links from toJoin2 to toJoin1
				for (int i: adjacent.get(toJoin2)) {
					if (i != toJoin1 && !adjacent.get(toJoin1).contains(i)) {
						adjacent.get(toJoin1).add(i);
					}
				}
				// update links to toJoin2 to toJoin1
				for (int i: adjacent.keySet()) {
					for (int k = 0; k < adjacent.get(i).size(); ++k) {
						if (adjacent.get(i).get(k) == toJoin2) {
							if (i != toJoin1 && !adjacent.get(i).contains(toJoin1)) {
								adjacent.get(i).set(k, toJoin1);
							} else {
								adjacent.get(i).remove(k);
							}
						}
					}
				}
			}
			// make this cluster not be considered anymore
			untouchable.add(ind1);
		}
		HashSet<Cluster> result = new HashSet<Cluster>();
		for (Cluster c: denseClusters) {
			result.add(c);
		}
		return result;
	}

	public HierarchicalCluster hierarchicalClustering() {
		return hierarchicalClustering(0, 2);
	}
	
	/**
	 * linkChoice: 0 -> minimum distance between two points in two clusters will be cluster distance<br>
	 * linkChoice: 1 -> maximum distance between two points in two clusters will be cluster distance<br>
	 * linkChoice: 2 -> average distance between two points in two clusters will be cluster distance<br>
	 * <br>
	 * distChoice: 0 -> maximum difference in dimensions is distance (equals distChoice == inf)<br>
	 * distChoice: else -> Math.pow(Math.pow(x_0, distChoice) + Math.pow(x_1, distChoice) + ..., 1 / distChoice)<br>
	 * -> Minkowsky-(distChoice)-distance<p>
	 * 
	 * deterministisches hierarchisches clustering<p>
	 * 
	 * kann dichte bereiche abbilden, auch hierarchien von clustern
	 */
	public HierarchicalCluster hierarchicalClustering(int linkChoice, int distChoice) {
		// setup a cluster for each element
    	ArrayList<HierarchicalCluster> clusters = new ArrayList<HierarchicalCluster>();
		for (Vector<Double> p: data) {
    		HashSet<Vector<Double>> c = new HashSet<Vector<Double>>();
    		c.add(p);
    		HierarchicalCluster cl = new HierarchicalCluster(c);
    		clusters.add(cl);
    	}
		int key = -1;
		// join closest clusters until the right number of clusters is achieved
		while (clusters.size() > 1) {
			// find closest clusters
			double min = Double.MAX_VALUE;
			double max = Double.MAX_VALUE;
			double avg = Double.MAX_VALUE;
			HierarchicalCluster minC1 = null;
			HierarchicalCluster minC2 = null;
			HierarchicalCluster maxC1 = null;
			HierarchicalCluster maxC2 = null;
			HierarchicalCluster avgC1 = null;
			HierarchicalCluster avgC2 = null;
			for (HierarchicalCluster c1: clusters) {
	    		for (HierarchicalCluster c2: clusters) {
	    			if (c1 == c2) {
	    				continue;
	    			}
	    			double min2 = Double.MAX_VALUE;
	    			double max2 = Double.MIN_VALUE;
	    			double sum2 = 0;
	    			int count2 = 0;
	    			HierarchicalCluster min2C1 = null;
	    			HierarchicalCluster min2C2 = null;
	    			HierarchicalCluster max2C1 = null;
	    			HierarchicalCluster max2C2 = null;
	        		for (Vector<Double> v1: c1.getDataSet()) {
	            		for (Vector<Double> v2: c2.getDataSet()) {
	            			double r = Double.MAX_VALUE;
	            			switch (distChoice) {
	            			case 0:
	            				r = maximumDist(v1, v2); // normal distance
	            				break;
	            			default:
	            				r = dist(v1, v2, distChoice); // normal, manhattan distance, etc.
	            			}
	            			/**
	            			 * not just calculate minimum of minimum distance between two points of two clusters
	            			 * but also calculate minimum of maximum distance between two points of two clusters
	            			 * and also calculate minimum of average distance between two points of two clusters
	            			 */
	            			if (r < min2) {
	            				min2 = r;
	            				min2C1 = c1;
	            				min2C2 = c2;
	            			}
	            			if (r > max2) {
	            				min2 = r;
	            				max2C1 = c1;
	            				max2C2 = c2;
	            			}
	            			sum2 += r;
	            			++count2;
	            		}
	        		}
	        		if (min2 < min) {
	        			min = min2;
        				minC1 = min2C1;
        				minC2 = min2C2;
	        		}
	        		if (max2 < max) {
	        			max = max2;
	        			maxC1 = max2C1;
	        			maxC2 = max2C2;
	        		}
	        		if (sum2 / count2 < avg) {
	        			avg = sum2 / count2;
        				avgC1 = c1;
        				avgC2 = c2;
	        		}
	    		}
			}
			// join closest clusters
			switch (linkChoice) {
			case 0:
				minC1.merge(minC2);
				minC1.setKey(++key);
				clusters.remove(minC2);
				break;
			case 1:
				maxC1.merge(maxC2);
				maxC1.setKey(++key);
				clusters.remove(maxC2);
				break;
			case 2:
				avgC1.merge(avgC2);
				avgC1.setKey(++key);
				clusters.remove(avgC2);
				break;
			}
		}
		return clusters.get(0);
	}

	/**
	 * deterministisches dichtebasiertes clustering<p>
	 * 
	 * braucht minPoints, epsilon<p>
	 * 
	 * kann zusammenhaengende formen erkennen
	 * 
	 * filtert noise
	 */
	public HashSet<Cluster> densityClustering(int minP, double eps) {
		// determine dense points
    	HashSet<Vector<Double>> internalP = new HashSet<Vector<Double>>();
    	for (Vector<Double> p: data) {
    		int pointNum = 0;
    		for (Vector<Double> q: data) {
    			if (dist(p, q) < eps) {
    				++pointNum;
    			}
    		}
    		if (pointNum >= minP) {
    			internalP.add(p);
    		}
    	}
    	// connect dense points if possible
    	ArrayList<HashSet<Vector<Double>>> clusters = new ArrayList<HashSet<Vector<Double>>>();
		for (Vector<Double> p: internalP) {
    		HashSet<Vector<Double>> c = new HashSet<Vector<Double>>();
    		c.add(p);
    		clusters.add(c);
    	}
    	boolean change = true;
    	while (change) {
    		change = false;
join:  		for (HashSet<Vector<Double>> c1: clusters) {
        		for (HashSet<Vector<Double>> c2: clusters) {
        			if (c1 == c2) {
        				continue;
        			}
            		for (Vector<Double> v1: c1) {
                		for (Vector<Double> v2: c2) {
                			if (dist(v1, v2) < eps) {
                				// join clusters
                				c1.addAll(c2);
                				clusters.remove(c2);
                				change = true;
                				break join;
                			}
                		}
            		}
        		}
    		}
    	}
    	// try to associate items at the border
    	HashSet<Vector<Double>> noise = new HashSet<Vector<Double>>();
    	noise.addAll(data);
    	for (HashSet<Vector<Double>> c: clusters) {
    		noise.removeAll(c);
    	}
    	for (HashSet<Vector<Double>> c: clusters) {
    		HashSet<Vector<Double>> clusterBorder = new HashSet<Vector<Double>>();
    		for (Vector<Double> p: c) {
    			for (Vector<Double> q: noise) {
        			if (dist(p, q) < eps) {
        				clusterBorder.add(q);
        			}
    			}
    		}
    		c.addAll(clusterBorder);
    		noise.removeAll(clusterBorder);
    	}
    	HashSet<Cluster> result = new HashSet<Cluster>();
    	for (int i = 0; i < clusters.size(); ++i) {
    		result.add(new Cluster(clusters.get(i)));
    	}
    	return result;
    }
 	
    /**
     * nicht-deterministisches partitionierendes clustering<p>
     * 
     * braucht clusteranzahl und ggf. anzahl der schritte oder schwellwert der veraenderung bei schritten zum abbruch<p>
     * 
     * kann nur klumpen abbilden
     */
    public HashSet<Cluster> kMeans(int k, int steps) {
 		// initialize solution
 		ArrayList<Vector<Double>> center = new ArrayList<Vector<Double>>();
 		ArrayList<HashSet<Vector<Double>>> solution = new ArrayList<HashSet<Vector<Double>>>();
 	 	for (int i = 0; i < k; ++i) {
 	 		Vector<Double> rand = null;
 	 		do {
 	 	 		int skip = (int)(Math.random() * data.size());
	 	 		for (Vector<Double> p: data) {
	 	 			if (skip == 0) {
	 	 				rand = p;
	 	 				break;
	 	 			}
	 	 			--skip;
	 	 		}
 	 		} while (center.contains(rand));
 	 		center.add(rand);
 	 	}
 	 	// do the first step
 	 	solution = associate(center, data);
 		center = extractNewCenters(solution);
 		// continue to iterate
 	 	for (int i = 1; i < steps; ++i) {
 	 		solution = associate(center, solution);
 	 		center = extractNewCenters(solution);
 	 	}
 	 	HashSet<Cluster> clustering = new HashSet<Cluster>();
 	 	for (int i = 0; i < solution.size(); ++i) {
 	 		clustering.add(new Cluster(solution.get(i)));
 	 	}
 		return clustering;
    }
    

 	private HashMap<Integer, HashSet<Vector<Double>>> makeGrid(int gridNum) {
 		return makeGrid(gridNum, false);
 	}
	
 	private HashMap<Integer, HashSet<Vector<Double>>> makeGrid(int gridNum, boolean filled) {
		// get overall borders
		ArrayList<Double> min = new ArrayList<Double>();
		ArrayList<Double> max = new ArrayList<Double>();
		for (int i = 0; i < dim; ++i) {
			min.add(Double.MAX_VALUE);
			max.add(Double.MIN_VALUE);
		}
		for (Vector<Double> p: data) {
			for (int i = 0; i < dim; ++i) {
				double val = p.get(i);
				if (val < min.get(i)) {
					min.set(i, val);
				}
				if (val > max.get(i)) {
					max.set(i, val);
				}
			}
		}
		// iterate over points, checking them into grids
		HashMap<Integer, HashSet<Vector<Double>>> grid = new HashMap<Integer, HashSet<Vector<Double>>>();
		for (Vector<Double> p: data) {
			ArrayList<Integer> position = new ArrayList<Integer>();
			for (int i = 0; i < dim; ++i) {
				double percentage = (p.get(i) - min.get(i)) / (max.get(i) - min.get(i));
				int pos = (int)(percentage * gridNum);
				if (pos == gridNum) {
					--pos;
				}
				position.add(pos);
			}
			// calculate integer code for the grid-cluster
			int code = 0;
			for (int i = 0; i < dim; ++i) {
				code += position.get(i) * Math.pow(gridNum, i);
			}
			if (grid.containsKey(code)) {
				grid.get(code).add(p);
			} else {
				HashSet<Vector<Double>> cluster = new HashSet<Vector<Double>>();
				cluster.add(p);
				grid.put(code, cluster);
			}
		}
		if (filled) {
			for (int i = 0; i < Math.pow(gridNum, dim); ++i) {
				if (!grid.containsKey(i)) {
					grid.put(i, new HashSet<Vector<Double>>());
				}
			}
		}
		return grid;
	}

	public HashSet<Cluster> kMeans(int k, int steps, int outOf) {
 		ArrayList<HashSet<Cluster>> results = new ArrayList<HashSet<Cluster>>();
 		ArrayList<Double> score = new ArrayList<Double>();
 		double highscore = Double.MIN_VALUE;
 		int index = -1;
 		for (int i = 0; i < outOf; ++i) {
 			results.add(kMeans(k, steps));
 			score.add(silh(results.get(results.size() - 1)));
 			if (score.get(score.size() - 1) > highscore) {
 				highscore = score.get(score.size() - 1);
 				index = i;
 			}
 		}
 		return results.get(index);
 	}
	
 	public HashSet<Cluster> kMeans(int from, int to, int steps, int stepsPerK) {
 		ArrayList<HashSet<Cluster>> solutions = new ArrayList<HashSet<Cluster>>();
 		ArrayList<Double> score = new ArrayList<Double>();
 		double highscore = Double.MIN_VALUE;
 		int highscoreK = -1;
 		for (int i = from; i <= to; ++i) {
 			solutions.add(kMeans(i, steps, stepsPerK));
 			score.add(silh(solutions.get(solutions.size() - 1)));
 			if (score.get(score.size() - 1) > highscore) {
 				highscore = score.get(score.size() - 1);
 				highscoreK = i - from;
 			}
 		}
		return solutions.get(highscoreK);
	}
	
 	public Vector<Double> plus(Vector<Double> a, Vector<Double> b) {
		if (a.size() != b.size() || a.size() != dim) {
			return null;
		}
		Vector<Double> c = new Vector<Double>();
		for (int i = 0; i < a.size(); ++i) {
			c.add(a.get(i) + b.get(i));
		}
		return c;
	}
	
 	public Vector<Double> minus(Vector<Double> a, Vector<Double> b) {
		if (a.size() != b.size() || a.size() != dim) {
			return null;
		}
		Vector<Double> c = new Vector<Double>();
		for (int i = 0; i < a.size(); ++i) {
			c.add(a.get(i) - b.get(i));
		}
		return c;
	}
	
 	public Vector<Double> by(Vector<Double> a, double b) {
		if (a.size() != dim || b == 0) {
			return null;
		}
		Vector<Double> c = new Vector<Double>();
		for (int i = 0; i < a.size(); ++i) {
			c.add(a.get(i) / b);
		}
		return c;
	}
 	
 	private double length(Vector<Double> a) {
 		return length(a, 2);
 	}
	
 	private double length(Vector<Double> a, int order) {
		if (a.size() != dim) {
			return Double.NaN;
		}
		double sum = 0;
		for (int i = 0; i < a.size(); ++i) {
			sum += Math.abs(Math.pow(a.get(i), order));
		}
		sum = Math.pow(sum, 1d / order);
		return sum;
	}
 	
	public HashSet<Cluster> kMeans() {
		return kMeans(data.size() / 10);
	}
	
	public HashSet<Cluster> kMeans(int minAvgClusterSize) {
		final int NUM_DATA = data.size();
		final int TEST_UP_TO = NUM_DATA / minAvgClusterSize;
		final int STEPS = 20; // per algorithm
		final int STEPS_PER_K = 1; // per tested K

 		int means = TEST_UP_TO;
 		ArrayList<HashSet<Cluster>> solutions = new ArrayList<HashSet<Cluster>>();
 		ArrayList<Double> score = new ArrayList<Double>();
 		double highscore = Double.MIN_VALUE;
 		int highscoreK = -1;
 		for (int i = 2; i <= means; ++i) {
 			solutions.add(kMeans(i, STEPS, STEPS_PER_K));
 			score.add(silh(solutions.get(solutions.size() - 1)));
 			if (score.get(i - 2) > highscore) {
 				highscore = score.get(score.size() - 1);
 				highscoreK = i;
 			}
 		}
	 	return solutions.get(highscoreK - 2);
    }
 	
 	// Silhouetten-Koeffizient
	public double silh(HashSet<Cluster> result) {
		HashMap<Cluster, Double> score = new HashMap<Cluster, Double>();
 		for (Cluster i: result) {
 			if (i.getDataSet().size() == 0) {
 				score.put(i, -1d);
 				continue;
 			}
 			double clusterSilh = 0;
 			for (Vector<Double> p: i.getDataSet()) {
 	 			Cluster secondClosest = null;
 	 			double minDist = Double.MAX_VALUE;
 	 			for (Cluster j: result) {
 	 				if (i == j) {
 	 					continue;
 	 				}
 	 				double dist = 0;
 	 				for (Vector<Double> p2: j.getDataSet()) {
 	 					dist += length(minus(p2, p));
 	 				}
 	 				dist /= j.getDataSet().size();
 	 				if (dist < minDist) {
 	 					minDist = dist;
 	 					secondClosest = j;
 	 				}
 	 			}
	 			double distA = 0;
	 			for (Vector<Double> p2: i.getDataSet()) {
	 				distA += length(minus(p2, p));
	 			}
	 			distA /= i.getDataSet().size();
	 			double distB = 0;
	 			for (Vector<Double> p2: secondClosest.getDataSet()) {
	 				distB += length(minus(p2, p));
	 			}
	 			distB /= secondClosest.getDataSet().size();
 	 			double silh = (distB - distA) / Math.max(distA, distB);
 	 			if (distA == 0) {
 	 				silh = 0;
 	 			}
 	 			clusterSilh += silh;
 			}
 			clusterSilh /= i.getDataSet().size();
 			score.put(i, clusterSilh);
 		}
 		double generalScore = 0;
 		int numData = 0;
 		for (Cluster i: score.keySet()) {
 			generalScore += score.get(i) * i.getDataSet().size();
 			numData += i.getDataSet().size();
 		}
 		return generalScore / numData;
 	}
 	
	private ArrayList<Vector<Double>> extractNewCenters(ArrayList<HashSet<Vector<Double>>> dataSets) {
 		int k = dataSets.size() / 2;
 		ArrayList<Vector<Double>> result = new ArrayList<Vector<Double>>();
 		for (int i = k - 1; i >= 0; --i) {
 	 		for (Vector<Double> c: dataSets.get(k + i)) {
 	 	 		result.add(c);
 	 		}
 	 		dataSets.remove(k + i);
 		}
 		return result;
 	}
 	
 	private ArrayList<HashSet<Vector<Double>>> associate(ArrayList<Vector<Double>> center, HashSet<Vector<Double>> data) {
 		int k = center.size();
 		ArrayList<HashSet<Vector<Double>>> result = new ArrayList<HashSet<Vector<Double>>>();
 		for (int i = 0; i < k; ++i) {
 			result.add(new HashSet<Vector<Double>>());
 		}
		for (Vector<Double> p: data) {
 			double minimumDistance = Double.MAX_VALUE;
 			int closestCluster = 0;
			for (int i = 0; i < k; ++i) {
 				double dist = dist(center.get(i), p);
 				if (dist < minimumDistance) {
 					minimumDistance = dist;
 					closestCluster = i;
 				}
 			}
			result.get(closestCluster).add(p);
 		}
 		for (int i = 0; i < k; ++i) {
 			result.add(new HashSet<Vector<Double>>());
 			Vector<Double> middle = new Vector<Double>();
 			for (int j = 0; j < dim; ++j) {
 				middle.add(0d);
 			}
 			for (Vector<Double> p: result.get(i)) {
 				middle = plus(middle, p);
 			}
 			middle = by(middle, result.get(i).size());
 			result.get(k + i).add(middle);
 		}
 		return result;
 	}
 	
 	private ArrayList<HashSet<Vector<Double>>> associate(ArrayList<Vector<Double>> center, ArrayList<HashSet<Vector<Double>>> dataSets) {
 		HashSet<Vector<Double>> data = new HashSet<Vector<Double>>();
 		for (HashSet<Vector<Double>> d: dataSets) {
 			data.addAll(d);
 		}
 		return associate(center, data);
 	}
 	
 	public double dist(Vector<Double> a, Vector<Double> b) {
 		return dist(a, b, 2);
 	}
 	
 	public double dist(Vector<Double> a, Vector<Double> b, int order) {
		return length(minus(a, b), order);
	}
	
	private double maximumDist(Vector<Double> v1, Vector<Double> v2) {
		double maxDist = 0;
		for (int i = 0; i < dim; ++i) {
			double dist = Math.abs(v1.get(i) - v2.get(i));
			if (dist > maxDist) {
				maxDist = dist;
			}
		}
		return maxDist;
	}

}
