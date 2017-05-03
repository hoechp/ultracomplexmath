package util.visuals;
import java.awt.*;
import java.util.HashSet;
import java.util.Vector;

import util.kd.clustering.Cluster;
import util.kd.clustering.Clustering;
import util.kd.clustering.HierarchicalCluster;


@SuppressWarnings("unused")
public class ClusteringDrawer extends java.applet.Applet implements Runnable {

	private static final int WIDTH = 800;
	private static final int HEIGHT = 600;
	private static final int SLEEP = 1000;
	
	private static final long serialVersionUID = 131449685649947953L;
	private Thread thread;
	private Image image;
	private Graphics2D graphics;

	private final int K = 10; // for actual clusters of random data
	
	private final int DIMENSION = 2;
	private final int NUM_DATA = 100;
	private final double REAL_CLUSTER_SIZE = 80;
	
	private HashSet<Vector<Double>> data;
	private HashSet<Cluster> finalClustering;
	private int displayedDimension = 0;

	public static Clustering generateRandomClusters(int dim, int k, int num, double maxVal, double clusterSize) {
 		// generate data
 		Clustering clustering = new Clustering(dim);
 		for (int i = 0; i < k; ++i) {
 			Vector<Double> realClusterCenter = new Vector<Double>();
 			for (int j = 0; j < dim; ++j) {
 	 			realClusterCenter.add(Math.random() * (maxVal - 2 * clusterSize) + clusterSize);
 			}
 			for (int j = i * num / k; j < (i + 1) * num / k; ++j) {
 	 			Vector<Double> addition = new Vector<Double>();
 				for (int o = 0; o < dim; ++o) {
 					addition.add((Math.random() * 2 - 1) * clusterSize);
 				}
 	 			clustering.addData(clustering.plus(realClusterCenter, addition));
 			}
 		}
 		return clustering;
	}

	public static Clustering generateRandomDensityClusters(int dim, int k, int num, double maxVal, double eps) {
		return null; // TODO
	}
	
	public static Clustering generateRandomHierarchyClusters(int dim, int k, int num, double maxVal) {
		return null; // TODO
	}
	
 	private void initStuff() {
 		// generate data
 		Clustering clustering = generateRandomClusters(DIMENSION, K, NUM_DATA, Math.min(WIDTH, HEIGHT), REAL_CLUSTER_SIZE);
 		data = clustering.getData();

 		//finalClustering = clustering.kMeans(20);
 		//finalClustering = clustering.kMeans(7, 50);
 		
 		
 		finalClustering = clustering.densityClustering(4, 60);
 		

 		//finalClustering = clustering.hierarchicalClustering(0, 0).toCluster(13);
 		//finalClustering = clustering.hierarchicalClustering(2, 1).toCluster(13);
 		//finalClustering = clustering.hierarchicalClustering().toCluster(13);
 		                                                                           

 		//finalClustering = clustering.subspaceClustering(7, 2);
 		

 		//finalClustering = HierarchicalCluster.hierarchicalClusterSetToClusterSet(clustering.gridClustering(10));
 		
 		/* *
 		HierarchicalCluster h = null;
 		for (HierarchicalCluster a: clustering.gridClustering(10)) {
 			if (h == null || a.getDataSet().size() > h.getDataSet().size()) {
 	 			h = a;
 			}
 		}
 		finalClustering = h.toCluster(10);
 		/* */
 		
	}
 	
 	private Color numColor(int i, int num) {
		double colorAngle = 2 * Math.PI * i / num;
		int r = (int)((Math.sin(colorAngle) / 2 + 0.5) * 255);
		int g = (int)((Math.sin(colorAngle + 2 * Math.PI / 3) / 2 + 0.5) * 255);
		int b = (int)((Math.sin(colorAngle + 4 * Math.PI / 3) / 2 + 0.5) * 255);
		if (i != num - 1 || num % 2 == 0) {
			int q1 = 3;
			int q2 = 5;
			if (i % 2 == 1) {
				r = r * q1 / q2;
				g = g * q1 / q2;
				b = b * q1 / q2;
			} else {
				r = 255 - r;
				g = 255 - g;
				b = 255 - b;
				r = r * q1 / q2;
				g = g * q1 / q2;
				b = b * q1 / q2;
				r = 255 - r;
				g = 255 - g;
				b = 255 - b;
			}
		}
		return new Color(r, g, b);
 	}
 	
 	private void drawPoint(Vector<Double> p, Color c) {
 		int dim1 = (2 * displayedDimension) % DIMENSION;
 		int dim2 = (2 * displayedDimension + 1) % DIMENSION;
 		graphics.setColor(c);
 		final int RADIUS = 5;
 		graphics.drawLine((int)p.get(dim1).doubleValue() - RADIUS, (int)p.get(dim2).doubleValue() - RADIUS, (int)p.get(dim1).doubleValue() + RADIUS, (int)p.get(dim2).doubleValue() + RADIUS);
 		graphics.drawLine((int)p.get(dim1).doubleValue() + RADIUS, (int)p.get(dim2).doubleValue() - RADIUS, (int)p.get(dim1).doubleValue() - RADIUS, (int)p.get(dim2).doubleValue() + RADIUS);
 		graphics.drawLine((int)p.get(dim1).doubleValue() - RADIUS + 1, (int)p.get(dim2).doubleValue() - RADIUS, (int)p.get(dim1).doubleValue() + RADIUS + 1, (int)p.get(dim2).doubleValue() + RADIUS);
 		graphics.drawLine((int)p.get(dim1).doubleValue() + RADIUS + 1, (int)p.get(dim2).doubleValue() - RADIUS, (int)p.get(dim1).doubleValue() - RADIUS + 1, (int)p.get(dim2).doubleValue() + RADIUS);
 		graphics.drawLine((int)p.get(dim1).doubleValue() - RADIUS, (int)p.get(dim2).doubleValue() - RADIUS + 1, (int)p.get(dim1).doubleValue() + RADIUS, (int)p.get(dim2).doubleValue() + RADIUS + 1);
 		graphics.drawLine((int)p.get(dim1).doubleValue() + RADIUS, (int)p.get(dim2).doubleValue() - RADIUS + 1, (int)p.get(dim1).doubleValue() - RADIUS, (int)p.get(dim2).doubleValue() + RADIUS + 1);
 		graphics.drawLine((int)p.get(dim1).doubleValue() - RADIUS - 1, (int)p.get(dim2).doubleValue() - RADIUS, (int)p.get(dim1).doubleValue() + RADIUS - 1, (int)p.get(dim2).doubleValue() + RADIUS);
 		graphics.drawLine((int)p.get(dim1).doubleValue() + RADIUS - 1, (int)p.get(dim2).doubleValue() - RADIUS, (int)p.get(dim1).doubleValue() - RADIUS - 1, (int)p.get(dim2).doubleValue() + RADIUS);
 		graphics.drawLine((int)p.get(dim1).doubleValue() - RADIUS, (int)p.get(dim2).doubleValue() - RADIUS - 1, (int)p.get(dim1).doubleValue() + RADIUS, (int)p.get(dim2).doubleValue() + RADIUS - 1);
 		graphics.drawLine((int)p.get(dim1).doubleValue() + RADIUS, (int)p.get(dim2).doubleValue() - RADIUS - 1, (int)p.get(dim1).doubleValue() - RADIUS, (int)p.get(dim2).doubleValue() + RADIUS - 1);
 	}
 	
	private void changeStuff() {
	}
	
 	private void drawGUI() {
 		// clear screen (black for better contrast on colors)
 		graphics.setColor(Color.gray);
 		graphics.fillRect(0, 0, WIDTH, HEIGHT);
 		// draw the initial data
 		for (Vector<Double> c: data) {
 			drawPoint(c, Color.black);
 		}
 		
 		int unusedClusters = 0;
 		for (Cluster i: finalClustering) {
 			if (i.getDataSet().size() == 0) {
 				++unusedClusters;
 			}
 		}
 		// draw the final solution
		int count = 0;
 		for (Cluster i: finalClustering) {
 			if (i.getDataSet().size() == 0) {
 				continue;
 			}
 			Color col = numColor(count, finalClustering.size() - unusedClusters);
 	 		++count;
 	 		for (Vector<Double> c: i.getDataSet()) {
 	 			drawPoint(c, col);
 	 		}
 		}
 		displayedDimension = (displayedDimension + 1) % DIMENSION;
	}
 	
	public void init() {
		image = createImage(800, 600);
		graphics = (Graphics2D)image.getGraphics();
		initStuff();
	}

	public void start () {
		thread = new Thread(this);
		thread.start();
	}

	public void run() {
		while (true) {
			repaint();
			changeStuff();
			try {
				Thread.sleep(SLEEP);
			} catch (InterruptedException e) {
			}
		}
	}

 	public void paint(java.awt.Graphics g) {
 		update(g);
 	}

 	public void update(java.awt.Graphics g) {
 		drawGUI();
 		// draw
 		g.drawImage(image, 0, 0, this);
 	}

	public void stop() {
 		thread = null;
 	}

}