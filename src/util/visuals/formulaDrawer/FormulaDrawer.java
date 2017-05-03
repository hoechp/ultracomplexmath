package util.visuals.formulaDrawer;

import java.awt.BorderLayout;
import java.awt.Button;
import java.awt.Canvas;
import java.awt.Color;
import java.awt.Component;
import java.awt.EventQueue;
import java.awt.Graphics2D;
import java.awt.Label;
import java.awt.TextField;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;

import javax.swing.JFrame;
import javax.swing.JPanel;
import javax.swing.JProgressBar;

import net.miginfocom.swing.MigLayout;
import util.hypercomplex.formula.FormulaSystem;
import util.hypercomplex.ultracomplex.Ultra;

public class FormulaDrawer {

	private JFrame frmHypercomplexFormulaDrawer;
	protected TextField textField_1;
	protected TextField textField_2;
	protected Component canvas;
	protected TextField textField_3;
	protected TextField textField;
	protected JProgressBar progressBar;
	protected boolean curvy = false;

	/**
	 * Launch the application.
	 */
	public static void main(String[] args) {
		EventQueue.invokeLater(new Runnable() {
			public void run() {
				try {
					FormulaDrawer window = new FormulaDrawer();
					window.frmHypercomplexFormulaDrawer.setVisible(true);
				} catch (Exception e) {
					e.printStackTrace();
				}
			}
		});
	}

	/**
	 * Create the application.
	 */
	public FormulaDrawer() {
		initialize();
	}
	
	public void drawPlot(final boolean curvy) {
		Thread thread = new Thread() {
			@Override
			public void run() {
				String text1 = textField_1.getText();
				String para1 = text1.substring(0, text1.indexOf(",")).trim();
				String text11 = text1.substring(text1.indexOf(",") + 1).trim();
				String para2 = text11.substring(0, text11.indexOf(",")).trim();
				String paraStep = text11.substring(text11.indexOf(",") + 1).trim();
				double minX = Double.parseDouble(para1);
				double maxX = Double.parseDouble(para2);
				int steps = Integer.parseInt(paraStep);
				String text2 = textField_2.getText();
				String para3 = text2.substring(0, text2.indexOf(",")).trim();
				String para4 = text2.substring(text2.indexOf(",") + 1).trim();
				double minRE = Double.parseDouble(para3);
				double maxRE = Double.parseDouble(para4);
				String text3 = textField_3.getText();
				String para5 = text3.substring(0, text3.indexOf(",")).trim();
				String para6 = text3.substring(text3.indexOf(",") + 1).trim();
				double minIM = Double.parseDouble(para5);
				double maxIM = Double.parseDouble(para6);
				double x = 0;

				int width = canvas.getWidth();
				int height = canvas.getHeight();
				Graphics2D g = (Graphics2D) canvas.getGraphics();
				g.clearRect(0, 0, width - 1, height - 1);
				g.setColor(Color.BLACK);
				g.drawRect(0, 0, width - 1, height - 1);

				FormulaSystem fs = new FormulaSystem(textField.getText() + " + (x - x)");
				
				Ultra lastValue = null;
				progressBar.setMinimum(0);
				progressBar.setMaximum(steps - 1);
				int x0 = (int)((0 - minRE) / (maxRE - minRE) * width);
				int y0 = (int)((0 - minIM) / (maxIM - minIM) * height);
				int cross = 5;
				g.setColor(Color.BLACK);
				g.drawLine(x0 - cross, y0 - cross, x0 + cross, y0 + cross);
				g.drawLine(x0 - cross, y0 + cross, x0 + cross, y0 - cross);
				int scaleSteps = 9;
				for (int j = 0; j < scaleSteps; ++j) {
					g.setColor(Color.LIGHT_GRAY);
					g.drawLine(0, j * height / (scaleSteps - 1), width, j * height / (scaleSteps - 1));
					g.drawLine(j * width / (scaleSteps - 1), 0, j * width / (scaleSteps - 1), height);
				}
				for (int i = 0; i < steps; ++i) {
					progressBar.setValue(i);
					x = ((double)i / (steps - 1) * (maxX - minX)) + minX;
					fs.set("x", "" + x);
					if (lastValue == null) {
						Ultra temp = fs.result();
						if (Double.isNaN(temp.getDouble(0))) {
							continue;
						}
						lastValue = temp;
					} else {
						Ultra temp = fs.result();
						if (Double.isNaN(temp.getDouble(0))) {
							continue;
						}
						Ultra thisValue = temp;
						int x1 = 0, x2 = 0, y1 = 0, y2 = 0, y1Black = 0, y2Black = 0;
						if (curvy) {
							x1 = (int)((lastValue.getDouble(0) - minRE) / (maxRE - minRE) * width);
							x2 = (int)((thisValue.getDouble(0) - minRE) / (maxRE - minRE) * width);
						} else {
							x1 = (int)((double)(i - 0.5) / steps * width);
							x2 = (int)((double)(i + 0.5) / steps * width);
							y1Black = height - (int)((lastValue.getDouble(0) + maxIM) / (maxIM - minIM) * height);
							y2Black = height - (int)((thisValue.getDouble(0) + maxIM) / (maxIM - minIM) * height);
						}
						y1 = height - (int)((lastValue.getDouble(7) + maxIM) / (maxIM - minIM) * height);
						y2 = height - (int)((thisValue.getDouble(7) + maxIM) / (maxIM - minIM) * height);
						g.setColor(Color.GRAY);
						g.drawLine(x1, y1, x2, y2);
						y1 = height - (int)((lastValue.getDouble(6) + maxIM) / (maxIM - minIM) * height);
						y2 = height - (int)((thisValue.getDouble(6) + maxIM) / (maxIM - minIM) * height);
						g.setColor(Color.CYAN);
						g.drawLine(x1, y1, x2, y2);
						y1 = height - (int)((lastValue.getDouble(5) + maxIM) / (maxIM - minIM) * height);
						y2 = height - (int)((thisValue.getDouble(5) + maxIM) / (maxIM - minIM) * height);
						g.setColor(Color.ORANGE);
						g.drawLine(x1, y1, x2, y2);
						y1 = height - (int)((lastValue.getDouble(4) + maxIM) / (maxIM - minIM) * height);
						y2 = height - (int)((thisValue.getDouble(4) + maxIM) / (maxIM - minIM) * height);
						g.setColor(Color.YELLOW);
						g.drawLine(x1, y1, x2, y2);
						y1 = height - (int)((lastValue.getDouble(3) + maxIM) / (maxIM - minIM) * height);
						y2 = height - (int)((thisValue.getDouble(3) + maxIM) / (maxIM - minIM) * height);
						g.setColor(Color.MAGENTA);
						g.drawLine(x1, y1, x2, y2);
						y1 = height - (int)((lastValue.getDouble(2) + maxIM) / (maxIM - minIM) * height);
						y2 = height - (int)((thisValue.getDouble(2) + maxIM) / (maxIM - minIM) * height);
						g.setColor(Color.BLUE);
						g.drawLine(x1, y1, x2, y2);
						y1 = height - (int)((lastValue.getDouble(1) + maxIM) / (maxIM - minIM) * height);
						y2 = height - (int)((thisValue.getDouble(1) + maxIM) / (maxIM - minIM) * height);
						g.setColor(Color.RED);
						g.drawLine(x1, y1, x2, y2);
						if (!curvy) {
							g.setColor(Color.BLACK);
							g.drawLine(x1, y1Black, x2, y2Black);
						}
						lastValue = thisValue;
					}
				}
				for (int j = 0; j < scaleSteps; ++j) {
					g.setColor(Color.BLACK);
					g.drawLine(0, j * height / (scaleSteps - 1), 5, j * height / (scaleSteps - 1));
					g.drawLine(j * width / (scaleSteps - 1), 0, j * width / (scaleSteps - 1), 5);
					String left = "";
					String top = "";
					left = "" + (-(double)j / (scaleSteps - 1) * (maxIM - minIM) - minIM);
					if (curvy) {
						top = "" + ((double)j / (scaleSteps - 1) * (maxRE - minRE) + minRE);
					} else {
						top = "" + ((double)j / (scaleSteps - 1) * (maxX - minX) + minX);
					}
					if (!(scaleSteps % 2 == 1 && (j == 0 || j == scaleSteps - 1))) {
						g.drawString(left, 9, j * height / (scaleSteps - 1) + 4);
						g.drawString(top, j * width / (scaleSteps - 1) - 9, 17);
					}
				}
			}
		};
		thread.start();
	}

	/**
	 * Initialize the contents of the frame.
	 */
	private void initialize() {
		frmHypercomplexFormulaDrawer = new JFrame();
		frmHypercomplexFormulaDrawer.setTitle("Hypercomplex Formula Drawer v1");
		frmHypercomplexFormulaDrawer.setBounds(100, 100, 450, 300);
		frmHypercomplexFormulaDrawer.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
		frmHypercomplexFormulaDrawer.getContentPane().setLayout(new BorderLayout(0, 0));
		
		canvas = new Canvas();
		frmHypercomplexFormulaDrawer.getContentPane().add(canvas, BorderLayout.CENTER);
		
		textField = new TextField();
		textField.setText("e^(x*pi*\u00EE)");
		frmHypercomplexFormulaDrawer.getContentPane().add(textField, BorderLayout.NORTH);
		
		progressBar = new JProgressBar();
		frmHypercomplexFormulaDrawer.getContentPane().add(progressBar, BorderLayout.SOUTH);
		
		JPanel panel = new JPanel();
		frmHypercomplexFormulaDrawer.getContentPane().add(panel, BorderLayout.EAST);
		panel.setLayout(new MigLayout("", "[70px]", "[22px][][][][][][][][]"));
		
		Label label = new Label("x_0, x_end, steps");
		panel.add(label, "cell 0 0");
		
		textField_1 = new TextField();
		textField_1.setText("-1, 1, 100");
		panel.add(textField_1, "cell 0 1,growx");
		
		Label label_1 = new Label("RE_min, RE_max");
		panel.add(label_1, "cell 0 2");
		
		textField_2 = new TextField();
		textField_2.setText("-2, 2");
		panel.add(textField_2, "cell 0 3,growx");
		
		Label label_2 = new Label("IM_min, IM_max");
		panel.add(label_2, "cell 0 4");
		
		textField_3 = new TextField();
		textField_3.setText("-2, 2");
		panel.add(textField_3, "cell 0 5,growx");
		
		final Button button = new Button("draw plot");
		button.addActionListener(new ActionListener() {
			public void actionPerformed(ActionEvent e) {
				final boolean curvyF = curvy;
				curvy = !curvy;
				if (curvy) {
					button.setLabel("draw plot (curvy)");
				} else {
					button.setLabel("draw plot");
				}
				drawPlot(curvyF);
			}
		});
		panel.add(button, "cell 0 6 1 3,grow");
	}

}
