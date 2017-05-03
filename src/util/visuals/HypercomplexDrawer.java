package util.visuals;
import java.awt.*;

import util.hypercomplex.Binary;
import util.hypercomplex.Complex;
import util.hypercomplex.Hypercomplex;
import util.hypercomplex.Dual;
import util.hypercomplex.M2R;
import util.hypercomplex.ultracomplex.Ultra;
import util.tests.Tests;

@SuppressWarnings("unused")
public class HypercomplexDrawer extends java.applet.Applet implements Runnable {

	private static final int WIDTH = 200;
	private static final int HEIGHT = 200;
	private static final int SLEEP = 10;
	
	private static final long serialVersionUID = 131449685649947953L;
	private Thread thread;
	private Image image;
	private Graphics2D graphics;
	
	// custom fields:

 	private void initStuff() {
 		drawGUI();
	}
 	private void changeStuff() {
	}
 	private void drawGUI() {
 		Ultra x1 = new Ultra(2, 3, 5, 7, 11, 13, 17, 19).by(10);
 		Ultra x2 = new Ultra(3, 5, 7, 11, 13, 17, 19, 2).by(10);
 		Ultra x3 = new Ultra(5, 7, 11, 13, 17, 19, 2, 3).by(10);
 		Ultra x4 = new Ultra(7, 11, 13, 17, 19, 2, 3, 5).by(10);
 		Ultra x5 = new Ultra(11, 13, 17, 19, 2, 3, 5, 7).by(10);
 		Ultra x6 = new Ultra(13, 17, 19, 2, 3, 5, 7, 11).by(10);
 		Ultra x7 = new Ultra(17, 19, 2, 3, 5, 7, 11, 13).by(10);
 		Ultra x8 = new Ultra(19, 2, 3, 5, 7, 11, 13, 17).by(10);
 		for (int x = 0; x < WIDTH; ++x) {
 	 		for (int y = 0; y < HEIGHT; ++y) {
 	 			double nX = ((double)x / WIDTH * 2 - 1) * Math.PI * 2;
 	 			double nY = ((double)y / HEIGHT * 2 - 1) * Math.PI * 2;
 	 			double fuzz = Math.PI / 64;
 	 			//Ultra c = new Ultra(nX, fuzz, nY, fuzz, fuzz, fuzz, fuzz, fuzz); // TODO configure
 	 			Ultra c = new Ultra(nX * 2 * Math.PI,
 	 					Math.sin(nY + 0 * 2 * Math.PI / 7) * 2 * Math.PI,
 	 					Math.sin(nY + 1 * 2 * Math.PI / 7) * 2 * Math.PI,
 	 					Math.sin(nY + 2 * 2 * Math.PI / 7) * 2 * Math.PI,
 	 					Math.sin(nY + 3 * 2 * Math.PI / 7) * 2 * Math.PI,
 	 					Math.sin(nY + 4 * 2 * Math.PI / 7) * 2 * Math.PI,
 	 					Math.sin(nY + 5 * 2 * Math.PI / 7) * 2 * Math.PI,
 	 					Math.sin(nY + 6 * 2 * Math.PI / 7) * 2 * Math.PI
 	 					); // TODO configure
 	 			double alpha = Math.PI / 8 * 2;
 	 			double beta = Math.PI / 16 * 2;
 	 			c = new Ultra(Math.cos(alpha) * nX, Math.sin(alpha) * nX, Math.cos(beta) * nY, 0, Math.sin(beta) * nY, 0, 0, 0);

 	 			//c = c.minus(x1).times(c.minus(x2)).times(c.minus(x3)).times(c.minus(x4))
 	 			//		.times(c.minus(x5)).times(c.minus(x6)).times(c.minus(x7)).times(c.minus(x8));
 	 			c = c.sin();
 	 			/*
 	 			c = c.times(c).times(c).times(c).times(c).times(c).times(c).times(x8).plus(
 	 				c.times(c).times(c).times(c).times(c).times(c).times(x7)).plus(
 	 				c.times(c).times(c).times(c).times(c).times(x6)).plus(
 	 				c.times(c).times(c).times(c).times(x5)).plus(
 	 				c.times(c).times(c).times(x4)).plus(
 	 				c.times(c).times(x3)).plus(
 	 				c.times(x2)).plus(
 	 				x1);
 	 			*/
 	 			
 	 			//System.out.println(c);
 	 			for (int i = 0; i < 4; ++i) {
 	 	 			drawComplex(c, graphics, x, y, i, i, WIDTH * i, 0);
 	 			}
 	 			
 	 			for (int i = 4; i < 8; ++i) {
 	 	 			drawComplex(c, graphics, x, y, i, i, WIDTH * (i - 4), HEIGHT);
 	 			}
 	 			
	 	 		drawComplex(c, graphics, x, y, -1, -1, WIDTH * 0, HEIGHT * 2);
	 	 		drawComplex(c, graphics, x, y, 0, 1, WIDTH * 1, HEIGHT * 2);
	 	 		drawComplex(c, graphics, x, y, 0, 2, WIDTH * 2, HEIGHT * 2);
	 	 		drawComplex(c, graphics, x, y, 0, 3, WIDTH * 3, HEIGHT * 2);

	 	 		drawComplex(c, graphics, x, y, 0, 4, WIDTH * 0, HEIGHT * 3);
	 	 		drawComplex(c, graphics, x, y, 0, 5, WIDTH * 1, HEIGHT * 3);
	 	 		drawComplex(c, graphics, x, y, 0, 6, WIDTH * 2, HEIGHT * 3);
	 	 		drawComplex(c, graphics, x, y, 0, 7, WIDTH * 3, HEIGHT * 3);
 	 			if (y % 40 == 0) {
 	 		 		System.out.println(((double)(x) + (double)(y) / HEIGHT) / WIDTH * 100 + "%");
 	 			}
 	 		}
 		}
 		graphics.setColor(Color.white);
 		//graphics.drawString("unnamed function plot", 10, 15);
 		//graphics.drawString("Ultra sin()", 10, 15);
	}
 	
 	public void drawComplex(Ultra c, Graphics2D g, int x, int y, int dim1, int dim2, int offsetX, int offsetY) {
 		double comp1 = dim1 < 0 || dim1 >= 8 ? c.length() : c.getDouble(dim1);
 		double comp2 = dim2 < 0 || dim2 >= 8 ? c.length() : c.getDouble(dim2);
		if (c != null) {
			Hypercomplex c2 = new Complex(comp1, comp2);
	 		graphics.setColor(c2.color());
	 		graphics.drawLine(x + offsetX, y + offsetY, x + offsetX, y + offsetY);
	 	} else {
	 		graphics.setColor(Color.black);
	 		graphics.drawLine(x + offsetX, y + offsetY, x + offsetX, y + offsetY);
	 	}
 	}
 	
	public void init() {
		image = createImage(WIDTH * 9, HEIGHT * 4);
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

}