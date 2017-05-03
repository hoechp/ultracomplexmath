package util.visuals;
import java.awt.*;

import util.hypercomplex.Binary;
import util.hypercomplex.Complex;
import util.hypercomplex.Hypercomplex;
import util.hypercomplex.Dual;
import util.hypercomplex.M2R;
import util.kd.clustering.Cluster;
import util.kd.clustering.Clustering;
import util.kd.clustering.HierarchicalCluster;
import util.tests.Tests;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.Vector;

@SuppressWarnings("unused")
public class ComplexClusteringTest extends java.applet.Applet implements Runnable {

	private static final int WIDTH = 200;
	private static final int HEIGHT = 150;
	private static final int SLEEP = 10;
	
	private static final long serialVersionUID = 131449685649947953L;
	private Thread thread;
	private Image image;
	private Graphics2D graphics;
	
	ArrayList<ArrayList<Hypercomplex>> data;
	Clustering clustering = new Clustering(4);
	Vector<Double> strechFactor = new Vector<Double>();
	
	// custom fields:

 	private void initStuff() {
 		strechFactor.add(1e0);
 		strechFactor.add(1e0);
 		strechFactor.add(1e3);
 		strechFactor.add(1e3);
 		drawGUI();
 		for (int xi = 0; xi < WIDTH; ++xi) {
 	 		for (int yi = 0; yi < HEIGHT; ++yi) {
 	 			Hypercomplex p = data.get(xi).get(yi);
 	 	 		Vector<Double> dataPoint = new Vector<Double>();
 	 	 		dataPoint.add(xi * strechFactor.get(0));
 	 	 		dataPoint.add(yi * strechFactor.get(1));
 	 	 		dataPoint.add(p.r() * strechFactor.get(2));
 	 	 		dataPoint.add(p.phi() * strechFactor.get(3));
 	 	 		clustering.addData(dataPoint);
 	 		}
 		}
	}
 	private void changeStuff() {
	}
 	private void drawGUI() {
 		data = new ArrayList<ArrayList<Hypercomplex>>();
 		for (int x = 0; x < WIDTH; ++x) {
 			data.add(new ArrayList<Hypercomplex>());
 	 		for (int y = 0; y < HEIGHT; ++y) {
 	 			// normalize 'x' Complex Dual Binary Complex.complex(c) Binary.binary(c) Dual.dual(c)
 	 			Hypercomplex c = new Complex(x - WIDTH / 2, y - HEIGHT / 2).by(Math.max(WIDTH / 2, HEIGHT / 2)).times(2 * Math.PI);
 	 			// use any kind of formula
 	 			/*c = c.pow(new Complex(1, 1).inverse());
 	 			c = Complex.complex(new M2R(  Dual.dual(c).tan()
 	 				     ).plus(new M2R(  Binary.binary(c).tan()
 	 				     ).plus(new M2R(Complex.complex(c).tan()
 	 				     ))).value().by(3));
 	 			*/
 	 			/*c = Complex.complex(new M2R(new Complex(2, 1)
	 				     ).pow(new M2R(Binary.binary(c)
	 				     )).value().ln());*/
 	 			//c = Complex.complex(new Complex("p", 1, -Math.PI / 4).times(c)).pow(new Complex(1, 1)); // turn by 45 degrees
 	 			c = Binary.binary(c).sin();
 	 			data.get(x).add(c);
 	 			drawComplex(c, graphics, x, y);
 	 		}
 		}
 		graphics.setColor(Color.white);
 		//graphics.drawString("unnamed function plot", 10, 15);
 		graphics.drawString("Binary c = c.sin()", 10, 15);
	}
 	
 	public Hypercomplex domainColorGrid(Hypercomplex c) {
		return domainColorGrid(c, 8, 1);
 	}
 	
 	public Hypercomplex domainColorGrid(Hypercomplex c, int n, double m) {
		// draw angles
		if (c != null)
		if (Math.abs((Complex.complex(c).eulerAngle() + 2 * Math.PI) % (2 * Math.PI / n)) < 0.01) {
			return null;
		}
		// draw intensities
		if (c != null &&
				Math.abs(Complex.complex(c).eulerLength() % (1 / m)) < 0.01) {
			return Complex.ZERO;
		}
		return c;
 	}
 	
 	public Hypercomplex domainColorGrid2(Hypercomplex c, int n, double m) {
		// draw angles
		if (c != null)
		if (Math.abs((Complex.complex(c).eulerAngle() + 2 * Math.PI) % (2 * Math.PI / n) - Math.PI / n) < 0.01) {
			return null;
		}
		// draw intensities
		if (c != null &&
				Math.abs(Complex.complex(c).eulerLength() % (1 / m) - 1 / (2 * m)) < 0.01) {
			return Complex.ZERO;
		}
		return c;
 	}
 	
 	public void drawComplex(Hypercomplex c, Graphics2D g, int x, int y) {
		if (c != null) {
	 		graphics.setColor(c.color());
	 		graphics.drawLine(x, y, x, y);
	 	} else {
	 		graphics.setColor(Color.black);
	 		graphics.drawLine(x, y, x, y);
	 	}
 	}
 	
	public void init() {
		image = createImage(WIDTH, HEIGHT);
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
 		// draw
 		g.drawImage(image, 0, 0, this);
 	}

	public void stop() {
 		thread = null;
 	}
	
	public boolean mouseUp(Event e, int x, int y) {
		System.out.println("start clustering"); // TODO
		HashSet<Cluster> result = clustering.kMeans(10, 20);
		System.out.println("done"); // TODO
		graphics.setColor(Color.black);
		graphics.fillRect(0, 0, WIDTH, HEIGHT);
		Cluster preSelected = null;
		int max = -1;
		for (Cluster c: result) {
			if (preSelected == null || c.getDataSet().size() > max) {
				preSelected = c;
				max = c.getDataSet().size();
			}
		}
		Cluster selected = null;
		for (Cluster c: result) {
			if (c != preSelected && (selected == null || c.getDataSet().size() > max)) {
				selected = c;
				max = c.getDataSet().size();
			}
		}
		double percentage = (double)selected.getDataSet().size() / clustering.getData().size() * 100;
		System.out.println(percentage + "% in cluster");
 		for (Vector<Double> v: selected.getDataSet()) {
	 		drawComplex(
		 			new Complex("p", v.get(2) / strechFactor.get(2), v.get(3) / strechFactor.get(3)),
		 			graphics,
		 			(int)((double)v.get(0) / strechFactor.get(0)),
		 			(int)((double)v.get(1) / strechFactor.get(1))
		 		);
 		}
		return true;
	}

}