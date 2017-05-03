package util.visuals;
import java.awt.*;

import util.hypercomplex.Complex;
import util.hypercomplex.Hypercomplex;

public class HypercomplexDrawer2 extends java.applet.Applet implements Runnable {

	private static final int WIDTH = 800;
	private static final int HEIGHT = 600;
	private static final int SLEEP = 20;
	
	private static final long serialVersionUID = 131449685649947953L;
	private Thread thread;
	private Image image;
	private Image image2;
	private Graphics2D graphics;
	private Graphics2D graphics2;
	private boolean wP, aP, sP, dP;
	private int x, y;
	
	// custom fields:

 	private void initStuff() {
 		x = WIDTH / 2;
 		y = HEIGHT / 2;
 		drawBG();
	}
 	private void changeStuff() {
 		if (wP) {
 			y -= 2;;
 		}
 		if (sP) {
 			y += 2;
 		}
 		if (aP) {
 			x -= 2;
 		}
 		if (dP) {
 			x += 2;
 		}
	}
 	
 	private void drawBG() {
 		for (int x = 0; x < WIDTH; ++x) {
 	 		for (int y = 0; y < HEIGHT; ++y) {
 	 			// normalize 'x' Complex Dual Binary Complex.complex(c) Binary.binary(c) Dual.dual(c)
 	 			Hypercomplex c = new Complex(x - WIDTH / 2, y - HEIGHT / 2).by(Math.max(WIDTH / 2, HEIGHT / 2)).times(2 * Math.PI);
 	 			c = f(c);
 	 			drawComplex(c, graphics2, x, y);
 	 		}
 		}
	}
 	
 	public void drawComplex(Hypercomplex c, Graphics2D g, int x, int y) {
		if (c != null) {
	 		g.setColor(c.color());
	 		g.drawLine(x, y, x, y);
	 	} else {
	 		g.setColor(Color.black);
	 		g.drawLine(x, y, x, y);
	 	}
 	}
 	
 	private void drawGUI() {
 		// clear
 		graphics.setColor(Color.white);
 		graphics.fillRect(0, 0, WIDTH, HEIGHT);
 		graphics.drawImage(image2, 0, 0, this);
 	 	// normalize 'x'
 		// Complex
 		// Dual
 		// Binary
 		// Complex.complex(c)
 		// Binary.binary(c)
 		// Dual.dual(c)
 		// Complex.complex(x);
 		// Binary.binary(x);
 		// Dual.dual(x);
 		int dist = 15;
 		//int grid = 5;
 		int grid = 0;
 		for (int i = -grid; i <= grid; ++i) {
 	 		for (int j = -grid; j <= grid; ++j) {
 	 	 	 	Hypercomplex c = new Complex(x - WIDTH / 2 + dist * i, y - HEIGHT / 2 + dist * j).by(Math.max(WIDTH / 2 + dist * i, HEIGHT / 2 + dist * j)).times(2 * Math.PI);
 	 	 	 	c = f(c);
 	 			//double intensity = (255d - (c.color().getRed() + c.color().getGreen() + c.color().getBlue()) / 3) / 255d;
 	 			//c = c.r0().times(intensity * 10);
 	 	 	 	drawComplex(c, graphics, x + dist * i, y + dist * j, 10);
 	 		}
 		}
	}
 	
 	Hypercomplex f(Hypercomplex x) {
			/*x = x.pow(new Complex(1, 1).inverse());
			x = Complex.complex(new M2R(  Dual.dual(x).tan()
				     ).plus(new M2R(  Binary.binary(x).tan()
				     ).plus(new M2R(Complex.complex(x).tan()
				     ))).value().by(3));*/
 		
 		
 		
			//return Complex.complex(x).sin();
			//return Binary.binary(x).sin();
 			//return Dual.dual(x).sin();
 		

 			return Complex.complex(x).cos().plus(Complex.complex(x).sin().times(Complex.I));
 			//return Binary.binary(x).cos().plus(Binary.binary(x).sin().times(Complex.I));
			//return Dual.dual(x).cos().plus(Dual.dual(x).sin().times(Complex.I));
 			//return Binary.binary(x).cos().plus(Complex.complex(Binary.binary(x).sin()).times(Complex.I));
 		
 		
			//return Complex.complex(new Complex("p", 1, -Math.PI / 4).times(x)).pow(new Complex(1, 1)); // turn by 45 degrees
			
 	}
 	
 	public void drawComplex(Hypercomplex c, Graphics2D g, int x, int y, double factor) {
 		graphics.setColor(Color.red);
 		graphics.drawLine(x - 5, y - 5, x + 5, y + 5);
 		graphics.drawLine(x - 5, y + 5, x + 5, y - 5);
		if (c != null) {
	 		int a = (int)(c.re() * factor);
	 		int b = (int)(c.im() * factor);
	 		graphics.setColor(Color.black);
	 		graphics.drawLine(x, y, a + x, b + y);
	 		graphics.setColor(Color.blue);
	 		graphics.drawLine((a + x) - 5, (b + y) - 5, (a + x) + 5, (b + y) + 5);
	 		graphics.drawLine((a + x) - 5, (b + y) + 5, (a + x) + 5, (b + y) - 5);
	 	}
 	}
 	
	public void init() {
		image = createImage(800, 600);
		image2 = createImage(800, 600);
		graphics = (Graphics2D)image.getGraphics();
		graphics2 = (Graphics2D)image2.getGraphics();
		initStuff();
	}

	public void start () {
		thread = new Thread(this);
		thread.start();
	}

	public void run() {
		while (true) {
	 		drawGUI();
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

	public boolean keyDown (Event e, int key) { // control
		switch (key) {
		case 1004:
		case 87:
		case 119:
			wP = true;
			sP = false;
			break;
		case 65:
		case 97:
			aP = true;
			dP = false;
		    break;
		case 1005:
		case 83:
		case 115:
			sP = true;
			wP = false;
		    break;
		case 68:
		case 100:
			dP = true;
			aP = false;
		    break;
		default:
			System.out.println("key integer value: " + key + "; char value: " + (char)key);
		}
		return true;
	}
  
	public boolean keyUp (Event e, int key) {
		switch (key) {
		case 1004:
		case 87:
		case 119: 
			wP = false;
			break;
		case 65:
		case 97:  
			aP = false;
			break;
		case 1005:
		case 83:
		case 115:  
			sP = false;
			break;
		case 68:
		case 100:  
			dP = false;
			break;
		}
		return true;
	}

}